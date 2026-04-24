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

FRIEND_API_URL = "https://task-api-1i5q.onrender.com/tasks"
FRIEND_TOKEN = "put-your-friend-jwt-token-here"

# ========== Helper: ตรวจสอบ JWT ==========
def verify_token():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None, jsonify({"error": {"code": 401, "message": "Unauthorized"}}), 401
    
    token = auth_header.split(" ")[1]
    try:
        # ใช้ algorithms=["HS256"] ตามที่คุณกำหนดไว้
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

# ========== 4. GET /external-tasks (ดึงข้อมูลเพื่อน) ==========
@app.route("/external-tasks", methods=["GET"])
def external_tasks():
    payload, err_response, err_code = verify_token()
    if err_response:
        return err_response, err_code
    
    external = []
    try:
        headers = {"Authorization": f"Bearer {FRIEND_TOKEN}"}
        # ลองดึงข้อมูลจาก API เพื่อน
        response = req.get(FRIEND_API_URL, headers=headers, timeout=5)
        if response.status_code == 200:
            # สมมติว่า API เพื่อนส่ง {"tasks": [...]} กลับมา
            external = response.json().get("tasks", [])
        else:
            external = {"error": f"Friend API returned {response.status_code}"}
    except Exception as e:
        external = {"error": f"Could not reach friend API: {str(e)}"}
    
    return jsonify({ 
        "my_tasks": tasks,
        "external_tasks": external
    }), 200

@app.route('/public-tasks', methods=['GET'])
def public_tasks():
    return jsonify({"tasks": tasks})
 

if __name__ == "__main__":
    app.run(debug=True, port=5000)