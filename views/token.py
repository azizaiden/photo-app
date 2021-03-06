from models import User
import flask_jwt_extended
from flask import Response, request
from flask_restful import Resource
import json
from datetime import timezone, datetime, timedelta

class AccessTokenEndpoint(Resource):

    def post(self):
        body = request.get_json() or {}
        print(body)
        username = body.get('username')
        password = body.get('password')
        if username is None or password is None:
            return Response(json.dumps({'message': 'Must include username and password.'}), mimetype="application/json", status=401)
        user = User.query.filter_by(username=username).one_or_none()
        if user is None:
            return Response(json.dumps({'message': 'Username or password is incorrect.'}), mimetype="application/json", status=401)
        if not user.check_password(password):
            return Response(json.dumps({'message': 'Username or password is incorrect.'}), mimetype="application/json", status=401)
        
        # check username and log in credentials. If valid, return tokens
        return Response(json.dumps({ 
            "access_token": flask_jwt_extended.create_access_token(identity=user.id), 
            "refresh_token": flask_jwt_extended.create_refresh_token(identity=user.id)
        }), mimetype="application/json", status=200)



class RefreshTokenEndpoint(Resource):
    '''if the refresh token is valid, return a new access token.
    Otherwise, return an error message.
    '''
    def post(self):

        body = request.get_json() or {}
        refresh_token = body.get('refresh_token')
        print(refresh_token)
        '''
        https://flask-jwt-extended.readthedocs.io/en/latest/refreshing_tokens/
        Hint: To decode the refresh token and see if it expired:
        decoded_token = flask_jwt_extended.decode_token(refresh_token)
        exp_timestamp = decoded_token.get("exp")
        current_timestamp = datetime.timestamp(datetime.now(timezone.utc))
        if current_timestamp > exp_timestamp:
            # token has expired:
            return Response(json.dumps({ 
                    "message": "refresh_token has expired"
                }), mimetype="application/json", status=401)
        else:
            # issue new token:
            return Response(json.dumps({ 
                    "access_token": "new access token goes here"
                }), mimetype="application/json", status=200)
        '''
        decoded_token = flask_jwt_extended.decode_token(refresh_token)
        print(decoded_token)
        exp_timestamp = decoded_token.get("exp")
        current_timestamp = datetime.timestamp(datetime.now(timezone.utc))
        if current_timestamp > exp_timestamp:
            # token has expired:
            return Response(json.dumps({ 
                    "message": "refresh_token has expired"
                }), mimetype="application/json", status=401)
        else:
            # issue new token:
            return Response(json.dumps({ 
                    "access_token": flask_jwt_extended.create_access_token(identity=decoded_token.get("sub"))
                }), mimetype="application/json", status=200)

        


def initialize_routes(api):
    api.add_resource(
        AccessTokenEndpoint, 
        '/api/token', '/api/token/'
    )

    api.add_resource(
        RefreshTokenEndpoint, 
        '/api/token/refresh', '/api/token/refresh/'
    )