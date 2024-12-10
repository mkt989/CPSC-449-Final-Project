import uuid
import redis
from flask import Flask, request, jsonify
app = Flask(__name__)
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def create_session(user_id: str):
   
    session_token = str(uuid.uuid4())
    redis_client.setex(f"session:{session_token}", 1800, user_id)  # Expires in 30 minutes
    return session_token