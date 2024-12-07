from functools import wraps
from flask import jsonify, request, current_app
import jwt
from app.models import User


#decorator method to make sure endpoints are jwt protected
def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'Alert!': "Token missing!"}), 403
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms= ['HS512', 'HS256'])
            current_user = User.query.filter_by(id=payload['user_id']).first()
        except:
            return jsonify({'Alert!': "Invalid token!"}), 403
        return func(current_user, *args, **kwargs)
    return decorated


#decorator method to make sure admin only endpoints are only accessed by admin
def admin_required(func):
    @wraps(func)
    def decorated(current_user, *args, **kwargs):
        if current_user.role != 'admin':
            return jsonify({"message" : "Access denied. Admin privileges only!"}), 403
        return func(current_user, *args, **kwargs)
    return decorated

# Decorator that restricts access to a view function for users only.
def user_only(func):
    @wraps(func)
    def decorated(current_user, *args, **kwargs):
        if current_user.role != 'user':
            return jsonify({"message" : "This is for users only!"}), 403
        return func(current_user, *args, **kwargs)
    return decorated