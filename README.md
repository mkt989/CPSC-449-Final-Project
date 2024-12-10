**Team members**:<br />
Samuel Luong 888059979<br />
Deborah Shaw 885136325<br />
Qing Gao 885087676<br />
Jose Diaz 886411032<br />

## Recipe Management

1. Add Recipe

Endpoint: /add-recipe

Method: POST

Description: Adds a new recipe to the database.

Authentication: Token required.

Request Body:
{
  "name": "Recipe Name",
  "ingredients": "List of ingredients",
  "instructions": "Preparation instructions",
  "preparation time": <integer>,
  "category": "Category Name",
  "Image URL": "URL to image"
}


