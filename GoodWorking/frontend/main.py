from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pymssql
import os
from dotenv import load_dotenv
import uvicorn

app = FastAPI()

# Clear terminal screen on changes made
os.system('cls')

# Load environment variables from .env file
load_dotenv()

# .env
# DB_USER=sa
# DB_PASSWORD=Admin@123.
# DB_NAME=vinDatabase
# DB_HOST=localhost

# Database connection parameters
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")

# Function to get a database connection
def get_db_connection():
    conn = pymssql.connect(server=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
    return conn

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
#    import uvicorn
#    uvicorn.run(app, host="0.0.0.0", port=8857)
    uvicorn.run(app, host="0.0.0.0", port=8857, ssl_keyfile=ssl_keyfile, ssl_certfile=ssl_certfile)

# uvicorn main:app --host 0.0.0.0 --port 8857 --reload --ssl-keyfile=certs/server_unencrypted.key --ssl-certfile=certs/server.crt
