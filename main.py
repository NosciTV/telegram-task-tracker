from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import os

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

DB_PATH = "tasks.db"
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'РІ СЂР°Р±РѕС‚Рµ',
    deadline TEXT
)
''')
conn.commit()
conn.close()

class Task(BaseModel):
    id: Optional[int]
    user_id: str
    title: str
    description: Optional[str] = ""
    status: Optional[str] = "РІ СЂР°Р±РѕС‚Рµ"
    deadline: Optional[str] = ""

@app.get("/tasks/{user_id}", response_model=List[Task])
def get_tasks(user_id: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM tasks WHERE user_id = ?", (user_id,))
    rows = c.fetchall()
    conn.close()
    return [Task(id=row[0], user_id=row[1], title=row[2], description=row[3], status=row[4], deadline=row[5]) for row in rows]

@app.post("/tasks", response_model=Task)
def add_task(task: Task):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO tasks (user_id, title, description, status, deadline) VALUES (?, ?, ?, ?, ?)",
              (task.user_id, task.title, task.description, task.status, task.deadline))
    task.id = c.lastrowid
    conn.commit()
    conn.close()
    return task

@app.patch("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task: Task):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE tasks SET title=?, description=?, status=?, deadline=? WHERE id=? AND user_id=?",
              (task.title, task.description, task.status, task.deadline, task_id, task.user_id))
    conn.commit()
    conn.close()
    task.id = task_id
    return task

# Serve static index.html for Telegram WebApp
app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/", response_class=FileResponse)
def root():
    return FileResponse("index.html")
