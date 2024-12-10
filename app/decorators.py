from functools import wraps
from flask import jsonify, request, current_app
import jwt
from app.models import User
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'Alert!': "Token missing!"}), 403
        
        # Retrieve the user_id from Redis
        user_id = redis_client.get(f"session:{token}")
        if not user_id:
            return jsonify({"Alert!": "Token expired or invalid!"}), 403

        # Query the database to get the User object
        current_user = User.query.get(user_id.decode("utf-8"))
        if not current_user:
            return jsonify({'Alert!': "User not found!"}), 404
        
        # Optionally, extend the expiration of the Redis session
        redis_client.expire(f"session:{token}", 1800)  # Extend for another 30 minutes
        
        return func(current_user, *args, **kwargs)
    return decorated
  


#decorator method to make sure admin only endpoints are only accessed by admin
def admin_required(func):
    @wraps(func)
    def decorated(current_user, *args, **kwargs):
        if current_user == None:
            return jsonify({"message" : "You must be logged in to access this."}), 403
        if current_user.role != 'admin':
            return jsonify({"message" : "Access denied. Admin privileges only!"}), 403
        return func(current_user, *args, **kwargs)
    return decorated
