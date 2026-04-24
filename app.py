from flask import Flask, request, jsonify
import jwt
import datetime
import requests as req

app = Flask(__name__)
SECRET_KEY = "MeowMeow666"

# ========== Data Storage (In-memory) ==========
USERS = {
    "student": "1234",
    "admin": "admin123"
}

tasks = [
    {"id": 1, "title": "Do homework", "status": "pending"},
    {"id": 2, "title": "Study Flask", "status": "done"}
]
next_id = 3
 
# ========== API เพื่อน 2 กลุ่ม ==========
# กลุ่มที่ 1 — ใส่ URL และ token ของกลุ่มแรก
FRIEND1_API_URL = "https://task-api1-mdz5.onrender.com/public-tasks"
FRIEND1_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoic3R1ZGVudCIsImV4cCI6MTc3NzAyNjA4Nn0.Zju5n8yBeaM7B8RGshv7xkz2iC374me_XL-MRG5RBUo"
 
# กลุ่มที่ 2 — ใส่ URL และ token ของกลุ่มสอง
FRIEND2_API_URL = "https://flask-api-mini-1.onrender.com/public-tasks"
FRIEND2_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc3NzAyMzEzMCwianRpIjoiNDg3NTBjN2UtZjJiMi00YWExLWFjMjgtMDUxMTQxODk4OWU4IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6ImFkbWluIiwibmJmIjoxNzc3MDIzMTMwLCJjc3JmIjoiNWY3NTVhMzAtMjZiNC00OTg4LWFiODAtMTdhMGQxNzdhZjU4IiwiZXhwIjoxNzc3MDI0MDMwfQ.RSChD8Z0yzqYkRFsSnXER9fOSwOsa_qzpXo4vg8KJWM"
def fetch_friend_tasks(url, token):
    try:
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        response = req.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("tasks") or data.get("data", [])
        else:
            return {"error": f"returned {response.status_code}"}
    except Exception as e:
        return {"error": f"ไม่สามารถเชื่อมได้: {str(e)}"}
 
# ========== Helper: ตรวจสอบ JWT ==========
def verify_token():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None, jsonify({"error": {"code": 401, "message": "Unauthorized"}}), 401
    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload, None, None
    except jwt.ExpiredSignatureError:
        return None, jsonify({"error": {"code": 401, "message": "Token expired"}}), 401
    except jwt.InvalidTokenError:
        return None, jsonify({"error": {"code": 401, "message": "Invalid token"}}), 401
 
# ========== 1. POST /login ==========
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": {"code": 400, "message": "Request body is required"}}), 400
 
    username = data.get("username")
    password = data.get("password")
 
    if not username or not password:
        return jsonify({"error": {"code": 400, "message": "Username and password are required"}}), 400
 
    if USERS.get(username) != password:
        return jsonify({"error": {"code": 401, "message": "Invalid credentials"}}), 401
 
    payload = {
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return jsonify({"token": token}), 200
 
# ========== 2. GET /tasks ==========
@app.route("/tasks", methods=["GET"])
def get_tasks():
    payload, err_response, err_code = verify_token()
    if err_response:
        return err_response, err_code
    return jsonify({"tasks": tasks}), 200
 
# ========== 3. POST /tasks ==========
@app.route("/tasks", methods=["POST"])
def create_task():
    global next_id
    payload, err_response, err_code = verify_token()
    if err_response:
        return err_response, err_code
 
    data = request.get_json()
    if not data:
        return jsonify({"error": {"code": 400, "message": "Request body is required"}}), 400
 
    title = data.get("title")
    if not title:
        return jsonify({"error": {"code": 400, "message": "Title is required"}}), 400
 
    status = data.get("status", "pending")
    new_task = {"id": next_id, "title": title, "status": status}
    tasks.append(new_task)
    next_id += 1
    return jsonify({"message": "Task created", "task": new_task}), 201
 
# ========== 4. GET /external-tasks ==========
@app.route("/external-tasks", methods=["GET"])
def external_tasks():
    payload, err_response, err_code = verify_token()
    if err_response:
        return err_response, err_code
 
    friend1_tasks = fetch_friend_tasks(FRIEND1_API_URL, FRIEND1_TOKEN)
    friend2_tasks = fetch_friend_tasks(FRIEND2_API_URL, FRIEND2_TOKEN)
 
    return jsonify({
        "my_tasks": tasks,
        "friend1_tasks": friend1_tasks,
        "friend2_tasks": friend2_tasks
    }), 200
 
# ========== Run ==========
if __name__ == "__main__":
    app.run(debug=True, port=5000)
