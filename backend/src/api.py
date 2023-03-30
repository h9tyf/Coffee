import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

#with app.app_context():
#    db_drop_and_create_all()

# ROUTES

@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks_all = Drink.query.all()
    if len(drinks_all) == 0:
        abort(404)
    
    drinks =  [drink.short() for drink in drinks_all]
    return jsonify({
            'success': True,
            'drinks': drinks
        })


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    drinks_all = Drink.query.all()
    if len(drinks_all) == 0:
        abort(404)
    
    drinks =  [drink.long() for drink in drinks_all]
    return jsonify({
            'success': True,
            'drinks': drinks
        })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):
    body = request.get_json()
    new_title = body.get("title", None)
    new_recipe = body.get("recipe", None)
    drink = Drink(title=new_title, recipe=new_recipe)
    drink.insert()

    return jsonify(
        {
            "success": True,
            "drinks": drink.long()
        })


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(payload, drink_id):
    drink = Drink.query.filter(Drink.id==drink_id).one_or_none()
    if drink is None:
        abort(404)
    body = request.get_json()
    new_title = body.get("title", None)
    new_recipe = body.get("recipe", None)
    drink.title = new_title
    drink.recipe = new_recipe
    drink.update()
    return jsonify({
        'success': True,
        'drinks': drink.long()
    })


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, drink_id):
    drink = Drink.query.filter(Drink.id==drink_id).one_or_none()
    if drink is None:
        abort(404)
    drink.delete()
    return jsonify({
        'success':True,
        'delete':drink_id
    })

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
