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
    # Check if user is already logged in
    user = request.session.get("user")
    if user:
        # If the user is logged in, redirect to the user page
        return RedirectResponse(url="/userpage")
    
    # If not logged in, check for an error message in query params
    error = request.query_params.get("error")
    return templates.TemplateResponse("main.html", {"request": request, "error": error})


@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    auth_result = authenticate(username, password)
    if auth_result is True:
        request.session["user"] = username  # Store username in session
        return RedirectResponse(url="/userpage", status_code=303)
    else:
        # Redirect back to "/" with an error message if authentication fails
        error_message = "Can't connect to server to validate user." if auth_result == "Can't connect to server to validate user." else "Invalid username or password"
        return RedirectResponse(url=f"/?error={error_message}", status_code=303)



@app.get("/logout")
async def logout(request: Request):
    request.session.pop("user", None)  # Clear the session
    return RedirectResponse(url="/")





@app.get("/userpage", response_class=HTMLResponse)
async def user_dashboard(request: Request):
    user = request.session.get("user")
    if user:
        return templates.TemplateResponse("authorized/userpage.html", {"request": request, "username": user})
    return RedirectResponse(url="/")

@app.get("/dashboard", response_class=HTMLResponse)
async def user_dashboard(request: Request):
    user = request.session.get("user")
    if user:
        return templates.TemplateResponse("authorized/dashboard.html", {"request": request, "username": user})
    return RedirectResponse(url="/")




