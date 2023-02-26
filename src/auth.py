from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from src.constants.http_status_code import HTTP_400_BAD_REQUEST\
    ,HTTP_409_CONFLICT, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_200_OK
from src.database import User, db
from flask_jwt_extended import create_access_token, create_refresh_token\
    , jwt_required, get_jwt_identity
import validators


auth = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


@auth.post('/register')
def register():
    username = request.json.get('username')
    email = request.json.get('email')
    password = request.json.get('password')

    if len(password)<8:
        
        return jsonify({
            'error': "Password is too short"
            }), HTTP_400_BAD_REQUEST

    if len(username)<4:
    
        return jsonify({
            'error': "Username is too short"
            }), HTTP_400_BAD_REQUEST

    if not username.isalnum() or " " in username:
    
        return jsonify({
            'error': "Username must be alphanumeric, also no spaces"
            }), HTTP_400_BAD_REQUEST
    
    if not validators.email(email):
        return jsonify({
            'error': "Email is not valid"
            }), HTTP_400_BAD_REQUEST
    
    if User.query.filter_by(email=email).first() is not None:
        return jsonify({
            'error': "Email is taken"
            }), HTTP_409_CONFLICT
    
    if User.query.filter_by(username=username).first() is not None:
        return jsonify({
            'error': "username is taken"
            }), HTTP_409_CONFLICT
    
    
    pwd_hash = generate_password_hash(password)

    user = User(username=username, password=pwd_hash,email=email)
    
    db.session.add(user)
    db.session.commit()



    return jsonify({
        "message":"User Created",
        "user" : {
            "username": username,
            "email" : email
        }
        }), HTTP_201_CREATED
        

@auth.post('/login')
def login():
    email = request.json.get('email', '')
    password = request.json.get('password', '')

    user = User.query.filter_by(email=email).first()

    if user:
        is_pass_correct = check_password_hash(user.password, password)

    if is_pass_correct:
        refresh = create_refresh_token(identity=user.id)
        access = create_access_token(identity=user.id)

        return jsonify({
            'user': {
                'refresh' : refresh,
                'access' : access,
                'username' : user.username,
                'email' : user.email                
            }
        }), HTTP_200_OK

    return jsonify({
        'error' : 'Wrong credentials'
    }), HTTP_401_UNAUTHORIZED



@auth.get('/me')
@jwt_required()
def me():
    user_id = get_jwt_identity()

    try:
        user = User.query.filter_by(id=user_id).first()

        return jsonify({
            "username" : user.username,
            "email" : user.email

                }), HTTP_200_OK
    
    except:
        return jsonify({
            'error' : 'User does not exist, or is invalid'
        }), HTTP_401_UNAUTHORIZED


@auth.post('/token/refresh')
@jwt_required(refresh=True)
def refresh_users_token():
    identity = get_jwt_identity()
    access =  create_access_token(identity=identity)

    return jsonify({
        'access' : access
    }), HTTP_200_OK