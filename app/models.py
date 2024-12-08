from .extensions import db, bcrypt

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(320), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False) 
    role = db.Column(db.String(20), default='user')
    
   # def __init__(self, password):
        #self.password = bcrypt.generate_password_hash(password)

class RecipeCategory(db.Model):
    __tablename__='categories'
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(50), nullable=False)

    recipes = db.relationship('Recipe', back_populates='category' ,cascade='all, delete-orphan')
    
class Recipe(db.Model):
    __tablename__ = 'recipes'
    id = db.Column(db.Integer, primary_key=True)
    recipe_name = db.Column(db.String(100), nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    prep_time = db.Column(db.Integer, nullable=False)  #Preparation time in minutes
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)  
    instructions = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)

    category = db.relationship('RecipeCategory', back_populates='recipes')

    ratings = db.relationship('RecipeRating', back_populates='recipe', cascade='all, delete-orphan')

class RecipeRating(db.Model):
    __tablename__ = 'recipe_ratings'

    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Float, nullable=False) 

    #Relationship with Recipe
    recipe = db.relationship('Recipe', back_populates='ratings')
