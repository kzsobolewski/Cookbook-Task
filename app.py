from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import datetime
import jwt
import os

# app init
app = Flask(__name__)

# database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# token key
app.config['SECRET_KEY'] = 'secretKey'

# association table
ingredients = db.Table(
    'ingredients',
    db.Column('ingredient_id',
              db.Integer,
              db.ForeignKey('ingredient.id'),
              primary_key=True,
              ),
    db.Column('recipe_id',
              db.Integer,
              db.ForeignKey('recipe.id'),
              primary_key=True,
              )
)

# recipe table
class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    description = db.Column(db.Text)
    durationInMinutes = db.Column(db.Integer)

    ingredients = db.relationship('Ingredient',
                                  secondary=ingredients,
                                  lazy='subquery',
                                  backref=db.backref('recipes', lazy=True),
                                  )

# ingredient table
class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

# decorator for token verification
def tokenRequired(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = None

        if 'token' in request.headers:
            token = request.headers['token']

        if not token:
            return {'message' : 'Token is missing'}, 401

        try:
            jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return {'message' : 'Token is invalid'}, 401

        return func(*args, **kwargs)
    return decorated


@app.route('/create-token', methods=['GET'])
def createToken():
    token = jwt.encode({'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=60)},
                       app.config['SECRET_KEY'])
    return {'token': token.decode('UTF-8')}

@app.route('/verify-token', methods=['GET'])
@tokenRequired
def verifyToken():
    return {'message': 'Token is valid'}, 200

@app.route('/recipe', methods=['GET'])
@tokenRequired
def getAllRecipes():
    recipeDict = {}
    for recipe in Recipe.query.all():
        recipeDict[recipe.id] = recipe.title
    return recipeDict, 200

@app.route('/ingredient', methods=['GET'])
@tokenRequired
def getAllIngredients():
    ingredientDict = {}
    for ingredient in Ingredient.query.all():
        ingredientDict[ingredient.id] = ingredient.name
    return ingredientDict

@app.route('/recipe/<recipe_id>', methods=['GET'])
@tokenRequired
def getRecipe(recipe_id):
    selectedRecipe = Recipe.query.filter_by(id=recipe_id).first()
    if not selectedRecipe :
        return {'message': 'Incorrect id'}
    ingredientList = []
    for ingredient in selectedRecipe.ingredients:
        ingredientList.append(ingredient.name)
    return {
        'title': selectedRecipe.title,
        'durationInMinutes': selectedRecipe.durationInMinutes,
        'description': selectedRecipe.description,
        'ingredients': ingredientList,
    }


# run server
if __name__ == "__main__":
    app.run(debug=True)

