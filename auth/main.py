from fastapi import FastAPI, Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from auth.authentication import authenticate

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")  # Replace with a strong secret key
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    auth_result = authenticate(username, password)
    if auth_result == True:
        request.session["user"] = username  # Store username in session
        return RedirectResponse(url="/userpage", status_code=303)
    elif auth_result == "Can't connect to server to validate user.":
        return templates.TemplateResponse("login.html", {"request": request, "error": auth_result})
    else:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid username or password"})






@app.post("/Xlogin", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if authenticate(username, password):
        request.session["user"] = username  # Store username in session
        return RedirectResponse(url="/userpage", status_code=303)
    else:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid username or password"})




@app.get("/userpage", response_class=HTMLResponse)
async def user_dashboard(request: Request):
    user = request.session.get("user")
    if user:
        return templates.TemplateResponse("userpage.html", {"request": request, "username": user})
    return RedirectResponse(url="/login")

@app.get("/dashboard", response_class=HTMLResponse)
async def user_dashboard(request: Request):
    user = request.session.get("user")
    if user:
        return templates.TemplateResponse("dashboard.html", {"request": request, "username": user})
    return RedirectResponse(url="/login")

@app.get("/logout")
async def logout(request: Request):
    request.session.pop("user", None)  # Clear the session
    return RedirectResponse(url="/")
