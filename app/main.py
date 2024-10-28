from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import sqlite3
import sys
import os
from dotenv import load_dotenv
import uvicorn
import datetime

# Initialize FastAPI app
app = FastAPI()

# Load environment variables from .env file
load_dotenv()

# Database file path
DB_FILE = os.getenv("DB_FILE", "db/entries.db")  # Default to 'db/entries.db' if not specified

# Function to get a database connection
def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # To return rows as dictionaries
    return conn

# Initialize the database and create the table with new columns if not exists
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT,
            serial_number TEXT,
            description TEXT,
            remarks TEXT,
            switch TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Run the database initialization
init_db()

# Mount static files
app.mount("/statics", StaticFiles(directory="statics"), name="statics")

# Initialize templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    distinct_word = os.getenv("DistinctWord")
    kb_patch = os.getenv("KBPatch")

    # Connect to SQLite database and retrieve entries
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM entries')
    saved_entries = cursor.fetchall()
    conn.close()

    return templates.TemplateResponse("index.html", {
        "request": request,
        "distinct_word": distinct_word,
        "kb_patch": kb_patch,
        "saved_entries": saved_entries
    })

@app.get("/api/entries")
async def get_entries():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM entries')
    entries = cursor.fetchall()
    conn.close()
    return [dict(entry) for entry in entries]

@app.post("/api/submit")
async def submit_entry(
    location: str = Form(...),
    serial_number: str = Form(...),
    description: str = Form(...),
    remarks: str = Form(...),
    switch: str = Form(...),
):
    # Generate a timestamp
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Connect to SQLite database and insert data into the new columns
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO entries (location, serial_number, description, remarks, switch, timestamp) 
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (location, serial_number, description, remarks, switch, timestamp))
    conn.commit()
    conn.close()

    # Redirect to the root endpoint
    return RedirectResponse(url='/', status_code=302)

# Define a Pydantic model for JSON submissions
class SubmitData(BaseModel):
    location: str
    serial_number: str
    description: str
    remarks: str
    switch: str

@app.post("/api/submit2")
async def submit_entry2(data: SubmitData):
    # Generate a timestamp
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Connect to SQLite database and insert data
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO entries (location, serial_number, description, remarks, switch, timestamp) 
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (data.location, data.serial_number, data.description, data.remarks, data.switch, timestamp))
    conn.commit()
    conn.close()

    return {"message": "Entry submitted successfully!", "data": data}

@app.delete("/api/delete/{entry_id}")
async def delete_entry(entry_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM entries WHERE id = ?', (entry_id,))
    conn.commit()
    conn.close()
    return {"message": "Entry deleted successfully."}



# New route to check for latest serial number entry
@app.get("/api/check_serial_number")
async def check_serial_number(serial_number: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM entries 
        WHERE serial_number = ? 
        ORDER BY timestamp DESC 
        LIMIT 1
    ''', (serial_number,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return dict(result)
    else:
        raise HTTPException(status_code=404, detail="Serial number not found")




if __name__ == "__main__":
    # Get port from command-line argument or use default 8857
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8857

    cert_dir = os.path.join(os.path.dirname(__file__), "certs")
    ssl_keyfile = os.path.join(cert_dir, "server_unencrypted.key")
    ssl_certfile = os.path.join(cert_dir, "server.crt")

    uvicorn.run(app, host="0.0.0.0", port=port, ssl_keyfile=ssl_keyfile, ssl_certfile=ssl_certfile)
