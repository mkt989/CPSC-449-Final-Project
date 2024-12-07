
from app.models import Recipe, Ingredient, RecipeIngredient
from app.decorators import token_required, user_only, admin_required
from flask import jsonify, request, Blueprint
from app.extensions import db

recipe_management_api = Blueprint('recipe_management_api', __name__)

@recipe_management_api.route('/add-recipe', methods=['POST'])
#@token_required
def add_recipe():
    recipe_name = request.json.get("name", None)
    instructions = request.json.get("instructions", "")
    new_recipe = Recipe(recipe_name=recipe_name, instructions=instructions)
    db.session.add(new_recipe)
    
    for ingredients in request.json.get("ingredients", None):
        ingredient_name = ingredients['name']
        quantity = ingredients['quantity']

        ingredient = Ingredient.query.filter_by(name=ingredient_name).first()
        if(ingredient == None):
            available_ingredients = [ingredient.name for ingredient in Ingredient.query.all()]
            return jsonify({
                "message" : "Unable find ingredient! The available ingredients are: " + ", ".join(available_ingredients)}), 409
        
        #Create new RecipeIngredient entry
        recipe_ingredient = RecipeIngredient(recipe_id=new_recipe.id, ingredient_id=ingredient.id, quantity=quantity)
        db.session.add(recipe_ingredient)
    db.session.commit()
    return jsonify({"message" : "%s has been added!" %new_recipe.recipe_name})

@recipe_management_api.route('/add-ingredient', methods=['POST'])
def add_ingredient():
    ingredient_name = request.json.get("name", None)
    if(ingredient_name == None):
        return jsonify({"message" : "Ingredient is required!"}), 404
    new_ingredient = Ingredient(name=ingredient_name)
    db.session.add(new_ingredient)
    db.session.commit()
    return jsonify({"message" : "%s is successfully added!" %new_ingredient.name})