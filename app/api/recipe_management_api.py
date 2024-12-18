
from app.models import Recipe, RecipeCategory, RecipeRating
from app.decorators import token_required, admin_required
from flask import jsonify, request, Blueprint
import requests
from app.extensions import db
import redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)
import json


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

    chosen_category = RecipeCategory.query.filter_by(
        category_name=category).first()
    if not chosen_category:
        return jsonify({"message": "%s does not exist!" % category}), 404
    if prep_time < 0:
        return jsonify({"message": "Preparation time cannot be negative!"}), 400
    if check_image(image_url):
        return jsonify({"message": "Invalid image URL!"}), 400
    new_recipe = Recipe(recipe_name=recipe_name, ingredients=ingredients, prep_time=prep_time,
                        category_id=chosen_category.id, instructions=instructions, user_id=current_user.id, image_url=image_url)
    db.session.add(new_recipe)
    db.session.commit()
    return jsonify({"message": "%s has been added!" % new_recipe.recipe_name})


@recipe_management_api.route('/update-recipe/<int:recipe_id>', methods=['PUT'])
@token_required
def update_recipe(current_user, recipe_id):
    recipe = Recipe.query.get(recipe_id)
    if not recipe or recipe.user_id != current_user.id:
        return jsonify({"message": "Recipe not found."})

    updated_recipe_data = request.get_json()
    for key, value in updated_recipe_data.items():
        if key == "category":
            category = RecipeCategory.query.filter_by(
                category_name=value).first()
            if category:
                recipe.category = category
            else:
                return jsonify({"message": "Category does not exist!"}), 404
        elif key == "category id":
            category = RecipeCategory.query.get(value)
            if category:
                recipe.category = category
            else:
                return jsonify({"message": "Invalid category ID."}), 400
        elif hasattr(recipe, key):  # check if the attribute exists in the db
            # update recipe attribute with new value
            setattr(recipe, key, value)
    db.session.commit()
    return jsonify({
        "message": "Successfully updated recipe!",
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
    cache_key = "all_recipes"
    cached_data = redis_client.get(cache_key)

    if cached_data:
        recipes_list = json.loads(cached_data)
        source="cache"
    else:
        recipes = Recipe.query.all()
        recipes_list = [
            {
                "id": recipe.id,
                "name": recipe.recipe_name,
                "category": recipe.category.category_name,
                "ingredients": recipe.ingredients,
                "preparation time": minutes_to_hours(recipe.prep_time),
                "instructions": recipe.instructions
            } 
            for recipe in recipes
        ]
        redis_client.setex(cache_key, 600, json.dumps(recipes_list))  # Cache for 10 minutes
        source="database"
    return jsonify({"source":source,"recipes": recipes_list}), 200


@recipe_management_api.route('/browse-recipes/<int:recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    
    # recipe = Recipe.query.get(recipe_id)
    # if not recipe:
    #     return jsonify({"Error": "Recipe not found"}), 404
    # response = {
    #     "id": recipe.id,
    #     "name": recipe.recipe_name,
    #     "category": recipe.category.category_name,
    #     "ingredients": recipe.ingredients,
    #     "preparation time": minutes_to_hours(recipe.prep_time),
    #     "instructions": recipe.instructions

    # }
    cache_key = f"recipe:{recipe_id}"
    cached_data = redis_client.get(cache_key)

    if cached_data:
        response = json.loads(cached_data)
        source="cache"
    else:
        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return jsonify({"Error": "Recipe not found"}), 404

        response = {
            "id": recipe.id,
            "name": recipe.recipe_name,
            "category": recipe.category.category_name,
            "ingredients": recipe.ingredients,
            "preparation time": minutes_to_hours(recipe.prep_time),
            "instructions": recipe.instructions
        }
        redis_client.setex(cache_key, 600, json.dumps(response))  # Cache for 10 minutes
        source="database"
    
    response["source"] = source
    return jsonify(response), 200


@recipe_management_api.route('/delete-recipe/<int:recipe_id>', methods=['DELETE'])
@token_required
def delete_recipe(current_user, recipe_id):
    recipe = Recipe.query.get(recipe_id)
    if recipe and recipe.user_id == current_user.id:
        db.session.delete(recipe)
        db.session.commit()
        return jsonify({"message": "Recipe successfully deleted!"})
    else:
        return jsonify({"message": "Recipe not found!"}), 404


@recipe_management_api.route('/add-category', methods=['POST'])
@token_required
@admin_required
def add_category(current_user):
    print("request.data:", request.data)  # Raw request body
    print("request.is_json:", request.is_json)  # Whether Flask thinks it's JSON
    print("request.json:", request.json)  # Parsed JSON data
    
    category_name = request.json.get("name", None)
    category = RecipeCategory.query.filter_by(
        category_name=category_name).first()
    if category:
        return jsonify({"message": "Category already exists!"}), 400
    if category_name == None:
        return jsonify({"message": "Category name is required!"}), 400
    new_category = RecipeCategory(category_name=category_name)
    db.session.add(new_category)
    db.session.commit()
    return jsonify({"message": "Category successfully added!"})


@recipe_management_api.route('/delete-category/<int:category_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_category(current_user, category_id):
    category = RecipeCategory.query.get(category_id)
    if category:
        db.session.delete(category)
        db.session.commit()
        return jsonify({"message": "category successfully deleted!"})
    else:
        return jsonify({"message": "category not found!"}), 404


@recipe_management_api.route('/categories', methods=['GET'])
def get_categories():
    categories = RecipeCategory.query.all()
    category_list = [
        {
            "category": category.category_name,
            "category id": category.id
        }
        for category in categories
    ]

    return jsonify({"categories": category_list})


@recipe_management_api.route('/filter-by-category', methods=['GET'])
def filter_recipes_by_category():
    # Get the category name from user input
    category_name = request.args.get('category', None)

    # Validate input
    if not category_name:
        return jsonify({"message": "Category name is required!"}), 400

    # Check if the category is in cache data
    cache_key = f"category:{category_name.lower()}"
    cached_data = redis_client.get(cache_key)

    if cached_data:
        recipes_list = json.loads(cached_data)
        source="cache"
    else:
        category = RecipeCategory.query.filter_by(
            category_name=category_name).first()
        if not category:
            return jsonify({"message": "Category not found!"}), 404

        # Query recipes for the specified category
        recipes = Recipe.query.filter_by(category_id=category.id).all()

        recipes_list = [
            {
                "id": recipe.id,
                "name": recipe.recipe_name,
                "prep_time": recipe.prep_time,
                "ingredients": recipe.ingredients,
                "instructions": recipe.instructions,
                "category": recipe.category.category_name,
                "image_url": recipe.image_url,
            }
            for recipe in recipes
        ]
        redis_client.setex(cache_key, 600, json.dumps(recipes_list))  # Cache for 10 minutes
        source="database"


    return jsonify({"source":source,"recipes": recipes_list}), 200


@recipe_management_api.route('/filter-by-preptime', methods=['GET'])
def filter_recipes_by_prep_time():
    # Get query from user input
    min_prep_time = request.args.get(
        'min', type=int, default=0)  # Default to 0
    max_prep_time = request.args.get(
        'max', type=int, default=None)  # Default to no upper limit

    # Validate input
    if min_prep_time < 0:
        return jsonify({"message": "Minimum preparation time cannot be negative!"}), 400

    # Query recipes within the specified prep time range
    query = Recipe.query.filter(Recipe.prep_time >= min_prep_time)
    if max_prep_time is not None:
        query = query.filter(Recipe.prep_time <= max_prep_time)

    recipes = query.all()

    recipes_list = [
        {
            "id": recipe.id,
            "name": recipe.recipe_name,
            "prep_time": recipe.prep_time,
            "ingredients": recipe.ingredients,
            "instructions": recipe.instructions,
            "category": recipe.category.category_name,
            "image_url": recipe.image_url,
        }
        for recipe in recipes
    ]

    return jsonify({"recipes": recipes_list}), 200


@recipe_management_api.route('/browse-by-rating', methods=['GET'])
def browse_by_rating():
    # Join recipes with their ratings, calculate average rating
    query = db.session.query(
        Recipe,
        db.func.coalesce(db.func.avg(RecipeRating.rating),
                         0).label("average_rating")
    ).outerjoin(RecipeRating).group_by(Recipe.id).order_by(db.desc("average_rating"))

    recipes = query.all()

    recipes_list = [
        {
            "id": recipe.id,
            "name": recipe.recipe_name,
            "category": recipe.category.category_name,
            "ingredients": recipe.ingredients,
            "prep_time": recipe.prep_time,
            "instructions": recipe.instructions,
            "average_rating": float(average_rating)
        }
        for recipe, average_rating in recipes
    ]

    return jsonify({"recipes": recipes_list}), 200


@recipe_management_api.route('/filter-by-rating', methods=['GET'])
def filter_by_rating():
    # Get the minimum rating from user input
    min_rating = float(request.args.get('min_rating', 0))  # Default is 0

    # Query recipes with their average ratings
    query = db.session.query(
        Recipe,
        db.func.coalesce(db.func.avg(RecipeRating.rating),
                         0).label("average_rating")
    ).outerjoin(RecipeRating).group_by(Recipe.id).having(db.func.coalesce(db.func.avg(RecipeRating.rating), 0) >= min_rating)

    recipes = query.all()

    recipes_list = [
        {
            "id": recipe.id,
            "name": recipe.recipe_name,
            "category": recipe.category.category_name,
            "ingredients": recipe.ingredients,
            "prep_time": recipe.prep_time,
            "instructions": recipe.instructions,
            "average_rating": float(average_rating)
        }
        for recipe, average_rating in recipes
    ]

    return jsonify({"recipes": recipes_list}), 200


@recipe_management_api.route('/add-rating/<int:recipe_id>', methods=['POST'])
@token_required
def add_rating(current_user, recipe_id):
    # Get the rating from the user input
    rating = request.json.get("rating", None)

    # Validate the rating
    if rating is None or not (0 <= rating <= 5):
        return jsonify({"message": "Rating must be between 0 and 5."}), 400

    # Check if the recipe exists
    recipe = Recipe.query.get(recipe_id)
    if not recipe:
        return jsonify({"message": "Recipe not found."}), 404

    # Check if the user has already rated the recipe
    existing_rating = RecipeRating.query.filter_by(
        recipe_id=recipe_id, user_id=current_user.id).first()
    if existing_rating:
        return jsonify({"message": "You have already rated this recipe. Please update your rating instead."}), 400

    # Add the rating
    new_rating = RecipeRating(
        recipe_id=recipe_id, user_id=current_user.id, rating=rating)
    db.session.add(new_rating)
    db.session.commit()

    return jsonify({
        "message": "Rating added successfully!",
        "recipe_id": recipe_id,
        "rating": rating
    }), 201


@recipe_management_api.route('/update-rating/<int:recipe_id>', methods=['PUT'])
@token_required
def update_rating(current_user, recipe_id):
    # Get the rating from user input
    new_rating = request.json.get("rating", None)

    # Validate the rating
    if new_rating is None or not (0 <= new_rating <= 5):
        return jsonify({"message": "Rating must be between 0 and 5."}), 400

    # Check if the recipe exists
    recipe = Recipe.query.get(recipe_id)
    if not recipe:
        return jsonify({"message": "Recipe not found."}), 404

    # Check if the user has already rated the recipe
    rating_entry = RecipeRating.query.filter_by(
        recipe_id=recipe_id, user_id=current_user.id).first()

    if rating_entry:
        # Update existing rating
        rating_entry.rating = new_rating
        message = "Rating updated successfully!"
    else:
        # Add a new rating entry
        rating_entry = RecipeRating(
            recipe_id=recipe_id, user_id=current_user.id, rating=new_rating)
        db.session.add(rating_entry)
        message = "Rating added successfully!"

    # Commit the changes
    db.session.commit()

    # Return a success message
    return jsonify({
        "message": message,
        "recipe_id": recipe_id,
        "new_rating": new_rating
    }), 200


@recipe_management_api.route('/delete-rating/<int:rating_id>', methods=['DELETE'])
@token_required
def delete_rating(current_user, rating_id):
    # Find the rating by ID
    rating = RecipeRating.query.get(rating_id)

    # Check if the rating exists
    if not rating:
        return jsonify({"message": "Rating not found."}), 404

    # Ensure the current user is the owner of the rating
    if rating.user_id != current_user.id:
        return jsonify({"message": "You can only delete your own ratings."}), 403

    # Delete the rating
    db.session.delete(rating)
    db.session.commit()

    return jsonify({"message": "Rating deleted successfully!"}), 200
