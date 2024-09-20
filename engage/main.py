from fastapi import FastAPI, Form, Request, HTTPException

from fastapi.responses import HTMLResponse

from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import sqlite3
import os
import uvicorn

# Initialize FastAPI app
app = FastAPI()

os.system('cls')

app.mount("/static", StaticFiles(directory="static"))  # Check directory name

# Initialize templates
templates = Jinja2Templates(directory="templates")

DB_FILE = f"./db/eventscore.db"

# Function to create a connection to the SQLite database
def get_connection():
    connection = sqlite3.connect(DB_FILE)
    return connection

# Function to create the scores table if it doesn't exist
def create_table1():
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY,
            Eid TEXT,
            EventNo TEXT,
            Score INTEGER,
            RecordedDateTime TEXT
        );
    """)
    connection.commit()
    connection.close()

# Create the scores table
create_table1()

@app.get("/submitscore")
async def submitscore(request: Request):
    return templates.TemplateResponse("vote2.html", {"request": request})


@app.get("/submitscore/{eventno}", response_class=HTMLResponse)
async def submitscore(eventno: str, request: Request):
    print(f"Event No: {eventno}")
    #return templates.TemplateResponse("vote2.html", {"request": request, "eventno": eventno})




# API endpoint to create a new entry
@app.post("/submitscore/")
def create_entry(
    Eid: str = Form(...), 
    EventNo: str = Form(...),
    Scores: str = Form(...)    
):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("INSERT INTO scores (Eid, EventNo, Score, RecordedDateTime) VALUES (?, ?, ?, ?)", 
                       (Eid, EventNo, Scores, current_time))
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        connection.close()

    return "Saved to SQLite Database successfully."

cert_dir = os.path.join(os.path.dirname(__file__), "certs")
ssl_keyfile = os.path.join(cert_dir, "server_unencrypted.key")
ssl_certfile = os.path.join(cert_dir, "server.crt")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8857, ssl_keyfile=ssl_keyfile, ssl_certfile=ssl_certfile)
