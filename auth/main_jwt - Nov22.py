


import sqlite3
import os





from fastapi import FastAPI, Form, Request, HTTPException, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from jose import jwt, JWTError
from datetime import datetime, timedelta
from auth.authentication import authenticate




from pprint import pprint









SECRET_KEY = "your-secret-key"  # Replace with a strong secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1  # Set token expiration as needed


# Database file path
DB_FILE = os.getenv("DB_FILE", "db/appdata.db")  # Default to 'db/entries.db' if not specified


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

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    error = request.query_params.get("error")
    token = request.cookies.get("access_token")
    if token:
        try:
            await get_current_user(request)
            return RedirectResponse(url="/userpage")
        except HTTPException:
            # Token is invalid, proceed to render login page
            return templates.TemplateResponse("main.html", {"request": request, "error": error})

    return templates.TemplateResponse("main.html", {"request": request, "error": error})



@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    auth_result = authenticate(username, password)
    if auth_result is True:
        access_token = create_access_token(data={"sub": username})
        response = RedirectResponse(url="/userpage", status_code=303)
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
    return templates.TemplateResponse("main.html", {"request": request, "error": str(exc.detail)})





# API PAGES ====================================================
#NEW Working
@app.get("/items", response_class=HTMLResponse)
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
    return templates.TemplateResponse("restricted/main_item.html", {
        "request": request,
        "distinct_word": distinct_word,
        "kb_patch": kb_patch,
        "saved_entries": saved_entries  # JSON-like format for use in the template
    })




# RESTRICTED PAGES ====================================================

@app.get("/userpage", response_class=HTMLResponse)
async def user_dashboard(request: Request, username: str = Depends(get_current_user)):
    return templates.TemplateResponse("restricted/userpage.html", {"request": request, "username": username})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, username: str = Depends(get_current_user)):
    return templates.TemplateResponse("restricted/dashboard.html", {"request": request, "username": username})

@app.get("/main_item", response_class=HTMLResponse)
async def dashboard(request: Request, username: str = Depends(get_current_user)):
    return templates.TemplateResponse("restricted/main_item.html", {"request": request, "username": username})












if __name__ == "__main__":
    # Get port from command-line argument or use default 8857
   # port = int(sys.argv[1]) if len(sys.argv) > 1 else 8857

    cert_dir = os.path.join(os.path.dirname(__file__), "certs")
    ssl_keyfile = os.path.join(cert_dir, "server_unencrypted.key")
    ssl_certfile = os.path.join(cert_dir, "server.crt")

    #uvicorn.run(app, host="0.0.0.0", port=port, ssl_keyfile=ssl_keyfile, ssl_certfile=ssl_certfile)
    uvicorn.run(app, host="0.0.0.0", port=8856, ssl_keyfile=ssl_keyfile, ssl_certfile=ssl_certfile)