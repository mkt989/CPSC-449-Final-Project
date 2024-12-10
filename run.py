from app import create_app, db
from flask import request, jsonify, Blueprint, current_app
app = create_app()

#initializing database
with app.app_context():
    db.create_all()
    
print(app.url_map)

@app.route('/test',methods=['GET'])
def test():
    return jsonify({"message":"success"}),200

if __name__ == "__main__":
    app.run(debug=True)