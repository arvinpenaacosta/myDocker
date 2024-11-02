import json
from fastapi import FastAPI, Request, Form, HTTPException

from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from fastapi.middleware.cors import CORSMiddleware

import sqlite3
import os
import datetime
from dotenv import load_dotenv
import uvicorn

from pprint import pprint
# Initialize FastAPI app
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing, change in production
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)



# Load environment variables from .env file
load_dotenv()

# Database file path
DB_FILE = os.getenv("DB_FILE", "db/appdata.db")  # Default to 'db/entries.db' if not specified

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
            types TEXT,
            macadd TEXT,
            remarks TEXT,
            status TEXT,
            switch TEXT,
            timestamp TEXT
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




#NEW Working API
#curl -k "URL/APIItems"
@app.get("/APIitems", response_class=JSONResponse)
async def read_items(request: Request):
    distinct_word = os.getenv("DistinctWord")
    kb_patch = os.getenv("KBPatch")

    # Connect to SQLite database and retrieve entries
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items")
    rows = cursor.fetchall()
    conn.close()

    # Convert rows to a list of dictionaries
    items = [dict(row) for row in rows]
    
    # Create pretty JSON string
    pretty_json = json.dumps(
        {"items": items, "distinct_word": distinct_word, "kb_patch": kb_patch},
        indent=4
    )

    # Return as an HTML response to view pretty JSON
    return HTMLResponse(content=f"<pre>{pretty_json}</pre>", media_type="text/html")

#curl -k "URL/APIItems"
@app.get("/APIitems2", response_class=JSONResponse)
async def read_items(request: Request):
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
    return saved_entries


#NEW Working
@app.get("/items", response_class=HTMLResponse)
async def read_items(request: Request):
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

    pprint(saved_entries["data"])

    # Return the response with the template
    return templates.TemplateResponse("item_maintBA.html", {
        "request": request,
        "distinct_word": distinct_word,
        "kb_patch": kb_patch,
        "saved_entries": saved_entries  # JSON-like format for use in the template
    })





@app.get("/items/check_serial/{serial_number}")
async def check_serial(serial_number: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items WHERE serial_number = ?", (serial_number,))
    item = cursor.fetchone()
    conn.close()
    if item:
        return JSONResponse({"item": dict(item)})
    return JSONResponse({"item": None})


@app.get("/items/check_item/{entry_id}")
async def check_serial(entry_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items WHERE id = ?", (entry_id,))
    item = cursor.fetchone()
    conn.close()
    if item:
        return JSONResponse({"item": dict(item)})
    return JSONResponse({"item": None})



@app.get("/items/all")
async def get_entries():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM items')
    entries = cursor.fetchall()
    conn.close()
    return [dict(entry) for entry in entries]






@app.post("/items/submit")
async def submit_entry(
    location: str = Form(...),
    serial_number: str = Form(...),
    brand: str = Form(None),
    model: str = Form(None),
    description: str = Form(...),
    types: str = Form(None),
    remarks: str = Form(...),
    status: str = Form(None),
    switch: str = Form(...),
):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if serial number exists to decide insert or update
    cursor.execute("SELECT * FROM items WHERE serial_number = ?", (serial_number,))
    existing_item = cursor.fetchone()

    if existing_item:
        # Update existing item
        cursor.execute('''
            UPDATE items SET location=?, brand=?, model=?, description=?, types=?, 
            remarks=?, status=?, switch=?, timestamp=? WHERE serial_number=?
        ''', (location, brand, model, description, types, remarks, status, switch, timestamp, serial_number))
        message = "Item updated successfully."
    else:
        # Insert new item
        cursor.execute('''
            INSERT INTO items (location, serial_number, brand, model, description, types, remarks, status, switch, timestamp) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (location, serial_number, brand, model, description, types, remarks, status, switch, timestamp))
        message = "Item added successfully."
    conn.commit()
    conn.close()

    print(message)

    return JSONResponse(content={"message": message})
    #return JSONResponse(content={"message": message, "redirect_url": "/items"})
    #return RedirectResponse(url='/items', status_code=302)



@app.delete("/items/delete/{entry_id}")
async def delete_entry(entry_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM items WHERE id = ?', (entry_id,))
    conn.commit()
    conn.close()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted successfully"}


# Disable an item by setting its switch to 0
@app.patch("/items/disable/{item_id}")
async def disable_item(item_id:  int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE items SET switch = 0 WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item disabled successfully"}






if __name__ == "__main__":
    # Get port from command-line argument or use default 8857
   # port = int(sys.argv[1]) if len(sys.argv) > 1 else 8857

    cert_dir = os.path.join(os.path.dirname(__file__), "certs")
    ssl_keyfile = os.path.join(cert_dir, "server_unencrypted.key")
    ssl_certfile = os.path.join(cert_dir, "server.crt")

    #uvicorn.run(app, host="0.0.0.0", port=port, ssl_keyfile=ssl_keyfile, ssl_certfile=ssl_certfile)
    uvicorn.run(app, host="0.0.0.0", port=8856, ssl_keyfile=ssl_keyfile, ssl_certfile=ssl_certfile)
