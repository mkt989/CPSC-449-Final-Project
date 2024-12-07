from .extensions import db, bcrypt

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(320), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False) 
    role = db.Column(db.String(20), default='user')
    
    def __init__(self, email, password, role='user'):
        self.email = email
        self.password = bcrypt.generate_password_hash(password)
        self.role = role

class Recipe(db.Model):
    __tablename__ = 'recipes'
    id = db.Column(db.Integer, primary_key=True)
    recipe_name = db.Column(db.String(100), nullable=False)
    instructions = db.Column(db.Text, nullable=False)

    ingredients = db.relationship('RecipeIngredient', back_populates='recipe')

class Ingredient(db.Model):
    __tablename__ = 'ingredients'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True,nullable=False)

    #establish relationship with RecipeIngredient
    recipe_ingredient = db.relationship('RecipeIngredient', back_populates='ingredient')

class RecipeIngredient(db.Model):
    __tablename__ ='recipe_ingredients'
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id'), primary_key=True)
    quantity = db.Column(db.String, nullable=False)

    #relationship with recipe and ingredient
    recipe = db.relationship('Recipe', back_populates='ingredients')
    ingredient = db.relationship('Ingredient', back_populates='recipe_ingredient')


