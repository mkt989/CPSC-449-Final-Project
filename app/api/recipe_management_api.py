
from app.models import Recipe, RecipeCategory, RecipeRating
from app.decorators import token_required, admin_required
from flask import jsonify, request, Blueprint
import requests
from app.extensions import db

recipe_management_api = Blueprint('recipe_management_api', __name__)

def check_image(url):
    try:
        response = requests.head(url, allow_redirects=True)   
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type')
            if content_type and content_type.startswith('image/'):
                return True
        return False
    except requests.exceptions.RequestException:  
        return False

@recipe_management_api.route('/add-recipe', methods=['POST'])
@token_required
def add_recipe(current_user):
    recipe_name = request.json.get("name", None)
    ingredients = request.json.get("ingredients", "")
    instructions = request.json.get("instructions", "")
    prep_time = request.json.get("preparation time", None)
    category = request.json.get("category", None)
    image_url = request.json.get("Image URL")

    chosen_category = RecipeCategory.query.filter_by(category_name=category).first()
    if not chosen_category:
        return jsonify({"message" : "%s does not exist!" %category}), 404
    if prep_time < 0:
        return jsonify({"message" : "Preparation time cannot be negative!"}), 400
    if check_image(image_url):
        return jsonify({"message" : "Invalid image URL!"}), 400
    new_recipe = Recipe(recipe_name=recipe_name, ingredients=ingredients, prep_time=prep_time, 
                        category_id=chosen_category.id, instructions=instructions, user_id=current_user.id,image_url=image_url)
    db.session.add(new_recipe)
    db.session.commit()
    return jsonify({"message" : "%s has been added!" %new_recipe.recipe_name})

@recipe_management_api.route('/update-recipe/<int:recipe_id>', methods=['PUT'])
@token_required
def update_recipe(current_user, recipe_id):
    recipe = Recipe.query.get(recipe_id)
    if not recipe or recipe.user_id != current_user.id:
        return jsonify({"message" : "Recipe not found."})
    
    updated_recipe_data = request.get_json()
    for key, value in updated_recipe_data.items():
        if key == "category":
            category = RecipeCategory.query.filter_by(category_name=value).first()
            if category:
                recipe.category = category
            else:
                return jsonify({"message" : "Category does not exist!"}), 404
        elif key == "category id":
            category = RecipeCategory.query.get(value)
            if category:
                recipe.category = category 
            else:
                return jsonify({"message": "Invalid category ID."}), 400
        elif hasattr(recipe, key): #check if the attribute exists in the db
            setattr(recipe, key, value) #update recipe attribute with new value
    db.session.commit()
    return jsonify({
        "message" : "Successfully updated recipe!",
        "updated_recipe": {
            "recipe_name": recipe.recipe_name,
            "ingredients": recipe.ingredients,
            "prep_time": minutes_to_hours(recipe.prep_time),
            "category": recipe.category.category_name,
            "category_id": recipe.category_id,
            "instructions": recipe.instructions,
            "image_url": recipe.image_url
        }  
            }), 200

def minutes_to_hours(minutes):
    hours = minutes // 60
    remaining_minutes = minutes % 60
    if hours < 1:
        return f"{minutes} minutes"
    else:
        return f"{hours} hours and {remaining_minutes} minutes"


@recipe_management_api.route('/browse-recipes', methods=['GET'])
def show_all_recipes():
    recipes = Recipe.query.all()

    recipes_list = [
        {
        "id" : recipe.id,
        "name" : recipe.recipe_name,
        "category" : recipe.category.category_name,
        "ingredients" : recipe.ingredients,
        "preparation time" : minutes_to_hours(recipe.prep_time),
        "instructions" : recipe.instructions    
        } 
        for recipe in recipes
    ]
    return jsonify({"recipes" : recipes_list}), 200

@recipe_management_api.route('/browse-recipes/<int:recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    recipe = Recipe.query.get(recipe_id)
    if not recipe:
        return jsonify({"Error": "Recipe not found"}), 404
    response = {
        "id" : recipe.id,
        "name" : recipe.recipe_name,
        "category" : recipe.category.category_name,
        "ingredients" : recipe.ingredients,
        "preparation time" : minutes_to_hours(recipe.prep_time),
        "instructions" : recipe.instructions
        
    }
    return jsonify(response), 200


@recipe_management_api.route('/delete-recipe/<int:recipe_id>', methods=['DELETE'])
@token_required
def delete_recipe(current_user, recipe_id):
    recipe = Recipe.query.get(recipe_id)
    if recipe and recipe.user_id == current_user.id:
        db.session.delete(recipe)
        db.session.commit()
        return jsonify({"message" : "Recipe successfully deleted!"})
    else:
        return jsonify({"message" : "Recipe not found!"}), 404
    
@recipe_management_api.route('/add-category', methods=['POST'])
@token_required
@admin_required
def add_category(current_user):
    category_name = request.json.get("name", None)
    category = RecipeCategory.query.filter_by(category_name=category_name).first()
    if category:
        return jsonify({"message": "Category already exists!"}), 400
    if category_name == None:
        return jsonify({"message" : "Category name is required!"}), 400
    new_category = RecipeCategory(category_name=category_name)
    db.session.add(new_category)
    db.session.commit()
    return jsonify({"message" : "Category successfully added!"})

@recipe_management_api.route('/delete-category/<int:category_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_category(current_user, category_id):
    category = RecipeCategory.query.get(category_id)
    if category:
        db.session.delete(category)
        db.session.commit()
        return jsonify({"message" : "category successfully deleted!"})
    else:
        return jsonify({"message" : "category not found!"}), 404
    

@recipe_management_api.route('/categories', methods=['GET'])
def get_categories():
    categories = RecipeCategory.query.all()
    category_list = [
        {
            "category" : category.category_name,
            "category id" : category.id
        }
        for category in categories
    ]

    return jsonify({"categories" : category_list})
