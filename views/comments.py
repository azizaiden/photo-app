from flask import Response, request
from flask_restful import Resource
from . import can_view_post
import json
from models import db, Comment, Post
from my_decorators import is_valid_int_delete, is_valid_comm, secure_bookmark
import flask_jwt_extended

class CommentListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    @flask_jwt_extended.jwt_required()
    @is_valid_comm
    @secure_bookmark
    def post(self):
        body = request.get_json()    
        text = body.get("text")
        post_id = body.get("post_id")
        user_id = self.current_user.id
        comment = Comment(text, user_id, post_id)
        db.session.add(comment)
        db.session.commit()
        return Response(json.dumps(comment.to_dict()), mimetype="application/json", status=201)
        
class CommentDetailEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user

    @flask_jwt_extended.jwt_required()
    @is_valid_int_delete
    def delete(self, id):
        comment = Comment.query.get(id)
        if not comment or comment.user_id != self.current_user.id:
            return Response(json.dumps({'message': 'Comment does not exist'}), mimetype="application/json", status=404)
       

        Comment.query.filter_by(id=id).delete()
        db.session.commit()
        serialized_data = {
            'message': 'Comment {0} successfully deleted.'.format(id)
        }
        return Response(json.dumps(serialized_data), mimetype="application/json", status=200)



def initialize_routes(api):
    api.add_resource(
        CommentListEndpoint, 
        '/api/comments', 
        '/api/comments/',
        resource_class_kwargs={'current_user': flask_jwt_extended.current_user}

    )
    api.add_resource(
        CommentDetailEndpoint, 
        '/api/comments/<id>', 
        '/api/comments/<id>',
        resource_class_kwargs={'current_user': flask_jwt_extended.current_user}
    )
