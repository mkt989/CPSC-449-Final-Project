
from app.extensions import db, bcrypt
from flask import Flask
from .api.recipe_management_api import recipe_management_api
from .api.user_authentication import user_authentication_api

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)
    bcrypt.init_app(app)

    app.register_blueprint(recipe_management_api, url_prefix='/recipes')
    app.register_blueprint(user_authentication_api, url_prefix='/users')
    return app

