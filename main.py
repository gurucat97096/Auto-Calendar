from fastapi import FastAPI, Form, Request, Response
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import sqlite3
import os

app = FastAPI()
templates = Jinja2Templates(directory="templates")

DB_PATH  = "events.db"
conn     =  sqlite3.connect(DB_PATH)
cursor   =  conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    password TEXT
);
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT,
    title TEXT,
    date TEXT,
    note TEXT
);
""")
conn.commit()
conn.close()

def get_user(request: Request):
    return request.cookies.get("user_email")

@app.get("/signup")
def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.post("/signup")
def signup(email: str = Form(...), password: str = Form(...)):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
        return RedirectResponse("/login", 302)
    except:
        return HTMLResponse("Email already exists", 400)

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login(response: Response, email: str = Form(...), password: str = Form(...)):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        if cursor.fetchone():
            response = RedirectResponse("/calendar", 302)
            response.set_cookie("user_email", email)
            return response
    return HTMLResponse("Login failed", 401)

@app.get("/calendar")
def show_calendar(request: Request):
    user = get_user(request)
    if not user:
        return RedirectResponse("/login")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT title, date, note FROM events WHERE user_email=? ORDER BY date", (user,))
        events = cursor.fetchall()
    return templates.TemplateResponse("calendar.html", {"request": request, "events": events, "user": user})

@app.get("/event/new")
def new_event_page(request: Request):
    user = get_user(request)
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse("event_form.html", {"request": request, "event": None})

@app.post("/event/new")
def create_event(title: str = Form(...), date: str = Form(...), note: str = Form(""), request: Request = None):
    user = get_user(request)
    if not user:
        return RedirectResponse("/login")
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO events (user_email, title, date, note) VALUES (?, ?, ?, ?)", (user, title, date, note))
    return RedirectResponse("/calendar", 302)

@app.get("/logout")
def logout(response: Response):
    response = RedirectResponse("/login", 302)
    response.delete_cookie("user_email")
    return response
