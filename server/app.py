#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        json = request.get_json()
        if 'username' in json:
            json_bio = None
            json_image = None
            if 'bio' in json:
                json_bio = json['bio']
            if 'image_url' in json:
                json_image = json['image_url']
            new_user = User(
                username=json['username'],
                bio =json_bio,
                image_url = json_image
            )
            new_user.password_hash = json['password']
            new_user_dict = new_user.to_dict()
            print(type(new_user_dict))
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id
            return new_user_dict,201
        else:
            return {"message": "Unprocessable Entity"}, 422 

class CheckSession(Resource):
    def get(self):
        print(session['user_id'])
        if session['user_id']:
            user_id = session['user_id']
            user = User.query.filter(User.id == user_id).first()
            user_info = {
                'username':user.username,
                'id':user.id,
                'image_url':user.image_url,
                'bio':user.bio
            }
            return user_info, 200
        else:
            print('no luck')
            return {"message":"Unathorized"}, 401

class Login(Resource):
    def post(self):
        user = request.get_json()           
        user_name = User.query.filter(User.username == user["username"]).first()
        if user_name:
            if user_name.authenticate(user['password']) == True:
                user_info = {
                    'username':user_name.username,
                    'id':user_name.id,
                    'image_url':user_name.image_url,
                    'bio':user_name.bio
                }
                session['user_id'] = user_name.id
                print(user_info)
                return user_info, 200
            else:
                return {"message":"Unathorized"}, 401
        else:
            return {"message":"Unathorized"}, 401

class Logout(Resource):
    def delete(post):
        if session['user_id']:
            print(session['user_id'])
            session['user_id'] = None
            return {"message":"No Content"}, 204
        return {"message":"Unathorized"}, 401

class RecipeIndex(Resource):
    def get(self):
        print(session['user_id'])
        if session['user_id']:
            recipes_user = Recipe.query.filter(Recipe.user_id == session['user_id']).all()
            print(f'{len(recipes_user)} doneeeeee')
            recipes = []
            for r in recipes_user:
                recipe_dict = {
                    'title': r.title,
                    'instructions':r.instructions,
                    'minutes_to_complete':r.minutes_to_complete,
                }
                recipes.append(recipe_dict)
            return recipes, 200
        return {'message':'Unathorized'}, 401
    
    def post(post):
        print(session['user_id'])
        if session['user_id']:
            data = request.get_json()
            if len(data['instructions']) >= 50:
                print(data)
                new_recipe = Recipe(
                    instructions=data['instructions'],
                    minutes_to_complete=data['minutes_to_complete'],
                    title=data['title']
                )
                new_recipe.user_id = session['user_id']
                print(new_recipe.instructions)
                new_recipe_dict = new_recipe.to_dict()
                db.session.add(new_recipe)
                db.session.commit()
                print('added recepe')
                return new_recipe_dict, 201
            return {"message":"Unprocessable Entity"}, 422
        return {'message':'Unathorized'}, 401
    

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
