
# Recipe Management API

This project is a **Recipe Management API** designed to facilitate the creation, browsing, categorization, and rating of recipes. Built with **Flask**, it allows users to perform **CRUD operations** on recipes and recipe categories while ensuring secure access through **token-based authentication**. The system incorporates **caching mechanisms** using Redis to enhance performance for frequent queries, supports user-based recipe ratings, and utilizes Redis for **session management**.

With a focus on scalability and usability, this API serves as a robust backend solution for recipe management applications.

---

## Dependencies and Setup Instructions

### Dependencies
Ensure you have the following dependencies installed:
- Flask: `pip install flask`
- Flask-JWT-Extended: `pip install flask-jwt-extended`
- Flask-SQLAlchemy: `pip install flask-sqlalchemy`
- Redis: Install Redis server and Python client: `pip install redis`

### Setup Instructions
1. Clone this repository.
2. Install the dependencies listed above using the provided `pip install` commands.
3. Start the Redis server: `redis-server`.
4. Run the Flask application: `flask run run.py`.

---

## Team Members
- **Samuel Luong** (ID: 888059979)
- **Deborah Shaw** (ID: 885136325)
- **Qing Gao** (ID: 885087676)
- **Jose Diaz** (ID: 886411032)

---

## Features

### Recipe Management
1. **Add Recipe**  
   **Endpoint**: `/add-recipe`  
   **Method**: `POST`  
   **Description**: Adds a new recipe to the database.  
   **Authentication**: Token required.  
   **Request Body**:
   ```json
   {
     "name": "Recipe Name",
     "ingredients": "List of ingredients",
     "instructions": "Preparation instructions",
     "preparation_time": <integer>,
     "category": "Category Name",
     "image_url": "URL to image"
   }
   ```
   **Response**:
   - **Success**: `{ "message": "<Recipe Name> has been added!" }`
   - **Failure**: Error message with relevant HTTP status codes.

2. **Update Recipe**  
   **Endpoint**: `/update-recipe/<int:recipe_id>`  
   **Method**: `PUT`  
   **Description**: Updates an existing recipe.  
   **Authentication**: Token required.  
   **Request Body**:
   ```json
   {
     "<field>": "<new value>",
     "category": "New Category Name"
   }
   ```
   **Response**:
   - **Success**: Returns the updated recipe details.
   - **Failure**: Error message with relevant HTTP status codes.

3. **Browse All Recipes**  
   **Endpoint**: `/browse-recipes`  
   **Method**: `GET`  
   **Description**: Retrieves all recipes with optional caching.  
   **Response**:
   ```json
   {
     "source": "cache or database",
     "recipes": [ { ...recipe details... } ]
   }
   ```

4. **Get Recipe by ID**  
   **Endpoint**: `/browse-recipes/<int:recipe_id>`  
   **Method**: `GET`  
   **Description**: Retrieves a specific recipe by ID with optional caching.  
   **Response**:
   ```json
   {
     "source": "cache or database",
     "id": <recipe_id>,
     "name": "Recipe Name",
     "...other fields..."
   }
   ```

5. **Delete Recipe**  
   **Endpoint**: `/delete-recipe/<int:recipe_id>`  
   **Method**: `DELETE`  
   **Description**: Deletes a recipe if owned by the current user.  
   **Authentication**: Token required.  
   **Response**:
   - **Success**: `{ "message": "Recipe successfully deleted!" }`
   - **Failure**: `{ "message": "Recipe not found!" }`

---

### Category Management
1. **Add Category**  
   **Endpoint**: `/add-category`  
   **Method**: `POST`  
   **Description**: Adds a new recipe category.  
   **Authentication**: Token and admin privileges required.  
   **Request Body**:
   ```json
   { "name": "Category Name" }
   ```
   **Response**:
   - **Success**: `{ "message": "Category successfully added!" }`
   - **Failure**: `{ "message": "Category already exists!" }`

2. **Delete Category**  
   **Endpoint**: `/delete-category/<int:category_id>`  
   **Method**: `DELETE`  
   **Description**: Deletes a category.  
   **Authentication**: Token and admin privileges required.  
   **Response**:
   - **Success**: `{ "message": "Category successfully deleted!" }`
   - **Failure**: `{ "message": "Category not found!" }`

3. **Get Categories**  
   **Endpoint**: `/categories`  
   **Method**: `GET`  
   **Description**: Retrieves all categories.  
   **Response**:
   ```json
   {
     "categories": [
       { "category": "Category Name", "category_id": <int> }
     ]
   }
   ```

4. **Filter Recipes by Category**  
   **Endpoint**: `/filter-by-category`  
   **Method**: `GET`  
   **Description**: Retrieves recipes within a specified category.  
   **Query Parameters**:
   - `category`: Name of the category.  
   **Response**:
   ```json
   {
     "source": "cache or database",
     "recipes": [ { ...recipe details... } ]
   }
   ```

---

### Rating Management
1. **Add Rating**  
   **Endpoint**: `/add-rating/<int:recipe_id>`  
   **Method**: `POST`  
   **Description**: Adds a rating for a recipe.  
   **Authentication**: Token required.  
   **Request Body**:
   ```json
   { "rating": <float (0-5)> }
   ```
   **Response**:
   - **Success**: `{ "message": "Rating added successfully!" }`
   - **Failure**: `{ "message": "You have already rated this recipe." }`

2. **Update Rating**  
   **Endpoint**: `/update-rating/<int:recipe_id>`  
   **Method**: `PUT`  
   **Description**: Updates the user's rating for a recipe.  
   **Authentication**: Token required.  
   **Request Body**:
   ```json
   { "rating": <float (0-5)> }
   ```
   **Response**:
   - **Success**: `{ "message": "Rating updated successfully!" }`

3. **Delete Rating**  
   **Endpoint**: `/delete-rating/<int:rating_id>`  
   **Method**: `DELETE`  
   **Description**: Deletes a rating.  
   **Authentication**: Token required.  
   **Response**:
   - **Success**: `{ "message": "Rating deleted successfully!" }`

---

### Filtering and Sorting
1. **Filter by Preparation Time**  
   **Endpoint**: `/filter-by-preptime`  
   **Method**: `GET`  
   **Description**: Retrieves recipes within a specified preparation time range.  
   **Query Parameters**:
   - `min`: Minimum preparation time (default: 0).  
   - `max`: Maximum preparation time (optional).  
   **Response**:
   ```json
   { "recipes": [ { ...recipe details... } ] }
   ```

2. **Browse by Rating**  
   **Endpoint**: `/browse-by-rating`  
   **Method**: `GET`  
   **Description**: Retrieves recipes sorted by average rating.  
   **Response**:
   ```json
   { "recipes": [ { ...recipe details, "average_rating": <float> } ] }
   ```

3. **Filter by Rating**  
   **Endpoint**: `/filter-by-rating`  
   **Method**: `GET`  
   **Description**: Retrieves recipes with an average rating above a specified value.  
   **Query Parameters**:
   - `min_rating`: Minimum average rating (default: 0).  
   **Response**:
   ```json
   { "recipes": [ { ...recipe details, "average_rating": <float> } ] }
   ```

---

## Caching Details
Caching is implemented using **Redis** for the following features:
1. **Session Management**: Redis is used to manage user sessions securely and efficiently.
2. **Browse All Recipes**: Cached results for frequent queries.
3. **Get Recipe by ID**: Cached individual recipes for quicker retrieval.
4. **Filter Recipes by Category**: Cached filtered results by category.

---
