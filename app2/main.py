from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3
import os
from dotenv import load_dotenv

app = FastAPI()

# Clear terminal screen on changes made
os.system('cls')

# Load environment variables from .env file
load_dotenv()

# Connect to SQLite database
db_path = os.path.join(os.getcwd(), 'db', 'database.db')
DATABASE_URL = os.getenv("DATABASE_URL", db_path)


conn = sqlite3.connect(DATABASE_URL)
cursor = conn.cursor()

# Ensure the table exists (create if necessary)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        field1 TEXT NOT NULL,
        field2 TEXT NOT NULL
    )
''')
conn.commit()

# Mount static files
app.mount("/statics", StaticFiles(directory="statics"), name="statics")

# Initialize templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    distinct_word = os.getenv("DistinctWord")
    kb_patch = os.getenv("KBPatch")

    # Connect to SQLite database
    conn = sqlite3.connect(DATABASE_URL)
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

@app.post("/api/submit")
async def submit_entry(field1: str = Form(...), field2: str = Form(...)):
    # Connect to SQLite database
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()

    # Insert data into the database
    cursor.execute('''
        INSERT INTO entries (field1, field2)
        VALUES (?, ?)
    ''', (field1, field2))
    conn.commit()
    conn.close()

    # Redirect to the root endpoint
    return RedirectResponse(url='/', status_code=302)

@app.get("/api/hello")
def read_hello():
    return {"Hello": "World"}

if __name__ == "__main__":
    import uvicorn
    #uvicorn.run(app, host="0.0.0.0", port=5985, ssl_keyfile="server_unencrypted.key", ssl_certfile="server.crt", reload=True)
    uvicorn.run(app, host="0.0.0.0", port=8856)
    
    #uvicorn app.main:app --host 0.0.0.0 --port 8856 --reload --ssl-keyfile=server_unencrypted.key --ssl-certfile=server.crt
