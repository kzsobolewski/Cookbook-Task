from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from json import dumps
import os

# app init
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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


class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))


# test get
@app.route('/', methods=['GET'])
def get():
    arr = [1,2,3]
    return make_response(jsonify(recipes = dumps(arr)))


# run server
if __name__ == "__main__":
    app.run(debug=True)

