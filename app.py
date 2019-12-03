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
def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = None
        if 'token' in request.headers:
            token = request.headers['token']
        if not token:
            return {'message': 'Token is missing'}, 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return {'message': 'Token is invalid'}, 401
        return func(*args, **kwargs)

    return decorated


@app.route('/login', methods=['GET'])
def create_token():
    auth = request.authorization
    if not auth:
        return {'message': 'Login required'}, 401, \
               {'WWW-Authenticate': 'Basic realm="Login Required2"'}

    token = jwt.encode({'user': auth.username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=1)},
                       app.config['SECRET_KEY'])
    return {'token': token.decode('UTF-8')}


@app.route('/verify-token', methods=['GET'])
@token_required
def verify_token():
    return {'message': 'Token is valid'}, 200


@app.route('/recipe', methods=['GET'])
@token_required
def get_all_recipes():
    recipeList = []
    for recipe in Recipe.query.all():
        recipeList.append({'id': recipe.id,
                           'title': recipe.title})
    return {'recipes': recipeList}, 200


@app.route('/ingredient', methods=['GET'])
@token_required
def get_all_ingredients():
    ingredientList = []
    for ingredient in Ingredient.query.all():
        ingredientList.append({'id': ingredient.id,
                               'name': ingredient.name})
    return {'ingredients': ingredientList}


@app.route('/recipe/<recipe_id>', methods=['GET'])
@token_required
def get_recipe(recipe_id):
    selected_recipe = Recipe.query.filter_by(id=recipe_id).first()
    if not selected_recipe:
        return {'message': 'Incorrect id'}, 401
    ingredient_list = []
    for ingredient in selected_recipe.ingredients:
        ingredient_list.append(ingredient.name)
    return {
        'title': selected_recipe.title,
        'durationInMinutes': selected_recipe.durationInMinutes,
        'description': selected_recipe.description,
        'ingredients': ingredient_list,
    }, 200


# run server
if __name__ == "__main__":
    app.run(debug=True)
