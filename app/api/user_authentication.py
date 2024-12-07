from app.extensions import db
from app.models import User
from flask import request, jsonify, Blueprint, current_app
from datetime import datetime, timedelta, timezone
import jwt
import re

user_authentication_api = Blueprint('user_authentication_api', __name__)

email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'


@user_authentication_api.route('/register', methods=['POST'])
def register_user():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    email = request.json.get("email", None)
    role = request.json.get("role", "user")

    if username == None:
        return jsonify({"message" : "Username is required!"}), 404
    elif User.query.filter_by(username=username).first():
        return jsonify({"message" : "Username already exists!"}), 409
    
    if email == None:
        return jsonify({"message" : "Email is required!"}), 404
    elif re.match(email_regex, email) == None:
        return jsonify({"message" : "Invalid email format!"}), 409
    elif User.query.filter_by(email=email).first():
        return jsonify({"message" : "Email already exists!"}), 409
    
    new_user = User(username=username, password=password, email=email, role=role)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message" : "User registered successfully!"}), 201

# Authenticates a user and generates a JWT token upon successful login.
@user_authentication_api.route('/login', methods=['POST'])
def login():
    user = User.query.filter_by(username=request.json.get('username', None)).first()
    if(user and user.password == request.json.get('password', None)):
        token = jwt.encode({
            'user_id': user.id,
            'expiration': str(datetime.now(timezone.utc) + timedelta(seconds=120))
        }, current_app.config['SECRET_KEY'])
        return jsonify({"token" : token}), 200
    else:
        return jsonify({"message" : "Invalid credentials"}), 401
