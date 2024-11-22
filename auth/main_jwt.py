
import json
import sqlite3
import os
import uvicorn





from fastapi import FastAPI, Form, Request, HTTPException, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse 
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles





from jose import jwt, JWTError
from datetime import datetime, timedelta
from auth.authentication import authenticate


# import datetime
from pydantic import BaseModel
from datetime import datetime
from dotenv import load_dotenv
from pprint import pprint
from tabulate import tabulate

from io import BytesIO
from typing import Optional







SECRET_KEY = "your-secret-key"  # Replace with a strong secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Set token expiration as needed


# Database file path
DB_FILE = os.getenv("DB_FILE", "db/appdata2.db")  # Default to 'db/entries.db' if not specified


app = FastAPI()

# Function to get a database connection
def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # To return rows as dictionaries
    return conn

# Initialize the database and create the table with updated columns if it does not exist
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            serial_number TEXT,
            location TEXT,
            brand TEXT,
            model TEXT,
            macadd TEXT,
            description TEXT,
            itypes TEXT,
            remarks TEXT,
            status TEXT,
            switch TEXT,
            stampTime TEXT
        )
    ''')

    conn.commit()
    conn.close()

# Run the database initialization
@app.on_event("startup")
def on_startup():
    init_db()



# Mount static files
app.mount("/statics", StaticFiles(directory="statics"), name="statics")

# Initialize templates
templates = Jinja2Templates(directory="templates")


# ===================================================================================================
# Pydantic model for item data
class Item(BaseModel):
    serial_number: str
    location: str
    brand: str
    model: str
    description: str
    itypes: str
    macadd: str
    remarks: str
    status: str
    switch: str
    #stampTime: datetime  # Ensure timestamp is included as a datetime field
    stampTime: str  # Ensure timestamp is included as a datetime field

# Function to create JWT token
def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + expires_delta})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Dependency to get current user from the token
async def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated1")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated2")
        return username
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token3")

# load Welcome Page - if Authenticated redirect to Dashboard
@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    error = request.query_params.get("error")
    token = request.cookies.get("access_token")
    if token:
        try:
            await get_current_user(request)
            return RedirectResponse(url="/dashboard")
        except HTTPException:
            # Token is invalid, proceed to render login page
            return templates.TemplateResponse("welcome.html", {"request": request, "error": error})

    return templates.TemplateResponse("welcome.html", {"request": request, "error": error})

# Login / Logout / Authorization Handler
@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    auth_result = authenticate(username, password)
    if auth_result is True:
        access_token = create_access_token(data={"sub": username})
        response = RedirectResponse(url="/dashboard", status_code=303)
        response.set_cookie(key="access_token", value=access_token, httponly=True, max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60)
        return response
    else:
        error_message = "Can't connect to server to validate user." if auth_result == "Can't connect to server to validate user." else "Invalid username or password"
        return RedirectResponse(url=f"/?error={error_message}", status_code=303)

@app.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/")
    response.delete_cookie("access_token")  # Clear JWT cookie
    return response

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        # Redirect to login page if not authenticated
        return RedirectResponse(url="/?error=you got expired.", status_code=303)
    return templates.TemplateResponse("welcome.html", {"request": request, "error": str(exc.detail)})




# RESTRICTED API PAGES ========================================
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, username: str = Depends(get_current_user)):
    return templates.TemplateResponse("restricted/dashboard.html", {"request": request, "username": username})


#NEW Working ==================================================
@app.get("/main_items", response_class=HTMLResponse)
async def read_items(request: Request, username: str = Depends(get_current_user)):
    distinct_word = os.getenv("DistinctWord")
    kb_patch = os.getenv("KBPatch")

    # Connect to SQLite database and retrieve entries
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items")
    rows = cursor.fetchall()
    conn.close()

    # Build the `saved_entries` structure in the desired `jsonData` format
    saved_entries = {
        "data": []
    }

    # Populate `saved_entries` with the required format
    for row in rows:
        item = {
            "rowspan": str(row[0]),  # Assumes `row[0]` is intended as the unique identifier or count for rowspan
            "iteminfo": [
                {  "data0": row[0], "data1": row[1], "data2": row[2], "data3": row[3], "data4": row[4], "data5": row[5]      }, 
                {  "data6": row[6], "data7": row[7], "data8": row[8], "data9": row[9], "data10": row[10], "data11": row[11]    }
            ]
        }
        saved_entries["data"].append(item)

    # Return the response with the template
    return templates.TemplateResponse("restricted/main_items.html", {
        "request": request,
        "distinct_word": distinct_word,
        "kb_patch": kb_patch,
        "saved_entries": saved_entries  # JSON-like format for use in the template
    })


#NEW Working ==================================================
@app.get("/master_items", response_class=HTMLResponse)
async def read_items(request: Request, username: str = Depends(get_current_user)):
    return templates.TemplateResponse("restricted/master_items.html", {"request": request})



# ================================ RESTFUL API for Items  ===============================

# FETCH All Items from the database
@app.get("/items", response_class=JSONResponse)
async def get_items():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items")
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()

    # = WORKING =============================================
    json_data = json.dumps(items, indent=4)
    print(json_data)

    # ==============================================
    # Prepare the headers
    headers = ['ID', 'Serial Number', 'Location', 'Brand', 'Model', 'Description', 'itypes', 'MAC Address', 'Remarks', 'Status', 'Switch', 'stampTime']

    # Extract the values for each row (data)
    rows = [[item['id'], item['serial_number'], item['location'], item['brand'], item['model'], item['description'], item['itypes'], item['macadd'], item['remarks'], item['status'], item['switch'], item['stampTime']] for item in items]

    # Print the table
    print(tabulate(rows, headers=headers, tablefmt='pretty'))
    # ==============================================

    return items

# FETCH ITEM Per ID  ============================================================================
@app.get("/items/{item_id}", response_class=JSONResponse)
async def get_item_by_id(item_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    item = cursor.fetchone()
    conn.close()
    if item:
        return dict(item)
    else:
        raise HTTPException(status_code=404, detail="Item not found")

# SAVE Endpoint ======================================================================================
@app.post("/item/save", response_model=Item)
async def save_item(item: Item):
 
    conn = get_db_connection()
    cursor = conn.cursor()



    #item.stampTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    item.stampTime = datetime.now()
    item.stampTime = item.stampTime.strftime("%Y-%m-%d %H:%M:%S")

     

    cursor.execute(
        "INSERT INTO items (serial_number, location, brand, model, description, itypes, macadd, remarks, status, switch, stampTime) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (item.serial_number, item.location, item.brand, item.model, item.description, item.itypes, item.macadd, item.remarks, item.status, item.switch, item.stampTime)
    )
    
    conn.commit()
    conn.close()
    return item

# UPDATE  endpoint ======================================================================================
@app.put("/items/{id}", response_model=Item)
async def update_item(id: int, item: Item):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    #item.stampTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    item.stampTime = datetime.now()
    item.stampTime = item.stampTime.strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute('''
        UPDATE items
        SET serial_number = ?, location = ?, brand = ?, model = ?, description = ?, itypes = ?, macadd = ?, remarks = ?, status = ?, switch = ?, stampTime = ?
        WHERE id = ?
    ''', (item.serial_number, item.location, item.brand, item.model, item.description, item.itypes,
          item.macadd, item.remarks, item.status, item.switch, item.stampTime, id))
    conn.commit()
    conn.close()

    return item

# DELETE  endpoint
@app.delete("/items/delete/{id}")
async def delete_item(id: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM items WHERE id = ?", (id,))
    item = cursor.fetchone()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    try:
        conn.execute("BEGIN")
        cursor.execute("DELETE FROM items WHERE id = ?", (id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete item")
    finally:
        conn.close()

    return {"message": "Item deleted successfully", "id": id}

# ================================ RESTFUL API for Items  ===============================

# API endpoint to check for a duplicate serial number
@app.get("/check-duplicate/{sernum}")
async def check_duplicate(sernum: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM items WHERE serial_number = ? LIMIT 1", (sernum,))
    exists = cursor.fetchone() is not None
    conn.close()

    if exists:  # Check if the serial number exists
        raise HTTPException(status_code=400, detail="Serial number already exists.")
    return {"message": "Serial number is available."}









if __name__ == "__main__":
    # Get port from command-line argument or use default 8857
   # port = int(sys.argv[1]) if len(sys.argv) > 1 else 8857

    cert_dir = os.path.join(os.path.dirname(__file__), "certs")
    ssl_keyfile = os.path.join(cert_dir, "server_unencrypted.key")
    ssl_certfile = os.path.join(cert_dir, "server.crt")

    #uvicorn.run(app, host="0.0.0.0", port=port, ssl_keyfile=ssl_keyfile, ssl_certfile=ssl_certfile)
    uvicorn.run(app, host="0.0.0.0", port=8856, ssl_keyfile=ssl_keyfile, ssl_certfile=ssl_certfile)