from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pymssql
import os
from dotenv import load_dotenv

app = FastAPI()

# Clear terminal screen on changes made
os.system('cls')

# Load environment variables from .env file
load_dotenv()

# Database connection parameters
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")

# Function to get a database connection
def get_db_connection():
    conn = pymssql.connect(server=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
    return conn

# Ensure the table exists (create if necessary)
def setup_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='entries' AND xtype='U')
        CREATE TABLE entries (
            id INT IDENTITY(1,1) PRIMARY KEY,
            field1 NVARCHAR(255) NOT NULL,
            field2 NVARCHAR(255) NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

setup_database()

# Mount static files
app.mount("/statics", StaticFiles(directory="statics"), name="statics")

# Initialize templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    distinct_word = os.getenv("DistinctWord")
    kb_patch = os.getenv("KBPatch")

    # Connect to SQL Server database
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

@app.post("/api/submit")
async def submit_entry(field1: str = Form(...), field2: str = Form(...)):
    # Connect to SQL Server database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert data into the database
    cursor.execute('''
        INSERT INTO entries (field1, field2)
        VALUES (%s, %s)
    ''', (field1, field2))
    conn.commit()
    conn.close()

    # Redirect to the root endpoint
    return RedirectResponse(url='/', status_code=302)

@app.get("/api/hello")
def read_hello():
    return {"Hello": "World"}

cert_dir = os.path.join(os.path.dirname(__file__), "certs")
ssl_keyfile = os.path.join(cert_dir, "server_unencrypted.key")
ssl_certfile = os.path.join(cert_dir, "server.crt")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8857)


# uvicorn main3:app --host 0.0.0.0 --port 8857 --reload --ssl-keyfile=certs/server_unencrypted.key --ssl-certfile=certs/server.crt
