# Mini Task Management API

REST API สำหรับจัดการ Task พัฒนาด้วย Python Flask พร้อม JWT Authentication

-----

## วิธีติดตั้งและรัน

bash
pip install -r requirements.txt
python app.py

API จะรันที่ http://localhost:5000

-----

## Endpoint List

|Method|Endpoint       |Auth Required|
|------|---------------|-------------|
|POST  |/login         |❌            |
|GET   |/tasks         |✅ JWT        |
|POST  |/tasks         |✅ JWT        |
|GET   |/external-tasks|✅ JWT        |

-----

## ตัวอย่าง Request / Response

### POST /login

**Request:**

json
{
  "username": "student",
  "password": "1234"
}

**Response:**

json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR..."
}

-----

### GET /tasks

**Header:**

Authorization: Bearer <token>

**Response:**

json
{
  "tasks": [
    { "id": 1, "title": "Do homework", "status": "pending" }
  ]
}

-----

### POST /tasks

**Header:**

Authorization: Bearer <token>

**Request:**

json
{
  "title": "Finish assignment",
  "status": "pending"
}

**Response:**

json
{
  "message": "Task created",
  "task": { "id": 3, "title": "Finish assignment", "status": "pending" }
}

-----

### GET /external-tasks

**Response:**

json
{
  "my_tasks": [...],
  "external_tasks": [...]
}

-----

## ตัวอย่าง Error

json
{ "error": { "code": 400, "message": "Title is required" } }
{ "error": { "code": 401, "message": "Unauthorized" } }
{ "error": { "code": 401, "message": "Token expired" } }

-----

## Deploy

แนะนำใช้ [Render](https://render.com) หรือ [PythonAnywhere](https://pythonanywhere.com)

### Deploy บน Render

1. Push โค้ดขึ้น GitHub
1. สร้าง Web Service บน Render
1. ใส่ Start Command: python app.py
1. Render จะให้ URL เช่น https://your-app.onrender.com