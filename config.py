import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", 'sqlite:///recipes.db') #temporary
    SECRET_KEY = os.getenv('SECRET_KEY')
    DEBUG = True