import json
from fastapi import FastAPI, Request, Form, HTTPException, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jose import jwt, JWTError
import sqlite3
import os
import datetime
from dotenv import load_dotenv
from datetime import timedelta
from auth.authentication import authenticate
import uvicorn

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Secret and algorithm for JWT
SECRET_KEY = "your-secret-key"  # Replace with a strong secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 5  # Set token expiration as needed

# Database file path
DB_FILE = os.getenv("DB_FILE", "db/appdata.db")



# Function to create a database connection
def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # To return rows as dictionaries
    return conn

# Database initialization
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

# Run database initialization on startup
@app.on_event("startup")
def on_startup():
    init_db()

# Mount static files
app.mount("/statics", StaticFiles(directory="statics"), name="statics")
# Initialize templates and static files
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
    stampTime: str  # Ensure timestamp is included as a datetime field




# JWT creation function
def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.datetime.utcnow() + expires_delta})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Dependency to get the current user from the token
async def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        return username
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

# Authentication-related endpoints
@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    auth_result = authenticate(username, password)
    if auth_result:
        access_token = create_access_token(data={"sub": username})
        response = RedirectResponse(url="/userpage", status_code=303)
        response.set_cookie(key="access_token", value=access_token, httponly=True, max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60)
        return response
    else:
        return RedirectResponse(url="/?error=Invalid username or password", status_code=303)

@app.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/")
    response.delete_cookie("access_token")
    return response

# Routes for item management (protected with JWT authentication)
@app.get("/APIitems", response_class=JSONResponse)
async def read_items(request: Request, username: str = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items")
    rows = cursor.fetchall()
    conn.close()
    
    items = [dict(row) for row in rows]
    return JSONResponse({"items": items})

@app.get("/items", response_class=HTMLResponse)
async def view_items(request: Request, username: str = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items")
    rows = cursor.fetchall()
    conn.close()

    saved_entries = {"data": [{"rowspan": str(row[0]), "iteminfo": [{"data0": row[0], "data1": row[1], "data2": row[2], "data3": row[3], "data4": row[4], "data5": row[5], "data6": row[6], "data7": row[7], "data8": row[8], "data9": row[9], "data10": row[10], "data11": row[11]}]} for row in rows]}
    
    return templates.TemplateResponse("main_item.html", {"request": request, "saved_entries": saved_entries})

@app.post("/items/submit")
async def submit_entry(request: Request, location: str = Form(...), serial_number: str = Form(...), brand: str = Form(None), model: str = Form(None), description: str = Form(...), types: str = Form(None), remarks: str = Form(...), status: str = Form(None), switch: str = Form(...), username: str = Depends(get_current_user)):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items WHERE serial_number = ?", (serial_number,))
    existing_item = cursor.fetchone()

    if existing_item:
        cursor.execute('''UPDATE items SET location=?, brand=?, model=?, description=?, types=?, remarks=?, status=?, switch=?, timestamp=? WHERE serial_number=?''', (location, brand, model, description, types, remarks, status, switch, timestamp, serial_number))
        message = "Item updated successfully."
    else:
        cursor.execute('''INSERT INTO items (location, serial_number, brand, model, description, types, remarks, status, switch, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (location, serial_number, brand, model, description, types, remarks, status, switch, timestamp))
        message = "Item added successfully."

    conn.commit()
    conn.close()
    return JSONResponse(content={"message": message})

@app.delete("/items/delete/{entry_id}")
async def delete_entry(entry_id: int, username: str = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM items WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted successfully"}

# Add other endpoints as necessary, applying `Depends(get_current_user)` to protect them

# Run the application with SSL if needed
if __name__ == "__main__":
    cert_dir = os.path.join(os.path.dirname(__file__), "certs")
    ssl_keyfile = os.path.join(cert_dir, "server_unencrypted.key")
    ssl_certfile = os.path.join(cert_dir, "server.crt")
    uvicorn.run(app, host="0.0.0.0", port=8856, ssl_keyfile=ssl_keyfile, ssl_certfile=ssl_certfile)
