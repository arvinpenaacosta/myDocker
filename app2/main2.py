from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from databases import Database
import os
from dotenv import load_dotenv

app = FastAPI()

# Clear terminal screen on changes made
os.system('cls')

# Load environment variables from .env file
load_dotenv()

# Connect to PostgreSQL database
DATABASE_URL = os.getenv("DATABASE_URL")
database = Database(DATABASE_URL)

async def connect_to_db():
    await database.connect()

async def disconnect_from_db():
    await database.disconnect()

# Ensure the table exists (create if necessary)
async def create_table():
    query = '''
        CREATE TABLE IF NOT EXISTS entries (
            id SERIAL PRIMARY KEY,
            field1 TEXT NOT NULL,
            field2 TEXT NOT NULL
        )
    '''
    await database.execute(query)

@app.on_event("startup")
async def startup():
    await connect_to_db()
    await create_table()

@app.on_event("shutdown")
async def shutdown():
    await disconnect_from_db()

# Mount static files
app.mount("/statics", StaticFiles(directory="statics"), name="statics")

# Initialize templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    distinct_word = os.getenv("DistinctWord")
    kb_patch = os.getenv("KBPatch")

    # Fetch entries from PostgreSQL database
    query = 'SELECT * FROM entries'
    saved_entries = await database.fetch_all(query)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "distinct_word": distinct_word,
        "kb_patch": kb_patch,
        "saved_entries": saved_entries
    })

@app.post("/api/submit")
async def submit_entry(field1: str = Form(...), field2: str = Form(...)):
    # Insert data into PostgreSQL database
    query = 'INSERT INTO entries (field1, field2) VALUES (:field1, :field2)'
    values = {"field1": field1, "field2": field2}
    await database.execute(query, values)

    # Redirect to the root endpoint
    return RedirectResponse(url='/', status_code=302)

@app.get("/api/hello")
def read_hello():
    return {"Hello": "World"}

if __name__ == "__main__":
    import uvicorn
    #uvicorn.run(app, host="0.0.0.0", port=5985, ssl_keyfile="server_unencrypted.key", ssl_certfile="server.crt", reload=True)
    uvicorn.run(app, host="0.0.0.0", port=8856)
