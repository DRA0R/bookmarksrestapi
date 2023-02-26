from flask import Blueprint, request, jsonify
from src.database import Bookmark, db
from src.constants.http_status_code import HTTP_400_BAD_REQUEST\
    , HTTP_409_CONFLICT, HTTP_201_CREATED, HTTP_200_OK, HTTP_404_NOT_FOUND\
    , HTTP_204_NO_CONTENT
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended.view_decorators import jwt_required
from flasgger import swag_from
import validators


bookmarks = Blueprint("bookmarks", __name__, url_prefix="/api/v1/bookmarks")

@bookmarks.route('/', methods=['POST', 'GET'])
@jwt_required()
def bookmark_view():


    current_user = get_jwt_identity()

    if request.method == 'POST':
        body = request.get_json().get('body', '')
        url = request.get_json().get('url', '')

        if not validators.url(url):
            return jsonify({
                'error' : 'Enter a valid url'
            }), HTTP_400_BAD_REQUEST
        
        if Bookmark.query.filter_by(url=url).first():
            return jsonify({
                'error' : 'url alredy exists'
            }), HTTP_409_CONFLICT
        

        bookmark = Bookmark(url=url, body=body, user_id=current_user)
        db.session.add(bookmark)
        db.session.commit()


        return jsonify({
            'id' : bookmark.id,
            'url' : bookmark.url,
            'short_url' : bookmark.short_url,
            'visit' : bookmark.visits,
            'body' : bookmark.body,
            'created_at' : bookmark.created_at,
            'updated_at' : bookmark.updated_at

            }),HTTP_201_CREATED
    
    else:

        page =  request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)

        bookmarks_data=Bookmark.query.filter_by(user_id=current_user).paginate(page=page, per_page=per_page)

        data = []
        
        for bookmark in bookmarks_data.items:
            data.append({
            'id' : bookmark.id,
            'url' : bookmark.url,
            'short_url' : bookmark.short_url,
            'visit' : bookmark.visits,
            'body' : bookmark.body,
            'created_at' : bookmark.created_at,
            'updated_at' : bookmark.updated_at

            })


        meta = {
            "page" : bookmarks_data.page,
            "pages" : bookmarks_data.pages,
            'total_count' : bookmarks_data.total,
            'prev_page' : bookmarks_data.prev_num,
            'next_page' : bookmarks_data.next_num,
            'has_next' : bookmarks_data.has_next,
            'has_prev' : bookmarks_data.has_prev

        }

        return jsonify({'data' : data, "meta" : meta}), HTTP_200_OK
    

@bookmarks.get("/<int:id>")
@jwt_required()
def get_bookmark(id):
    current_user = get_jwt_identity()

    bookmark = Bookmark.query.filter_by(user_id=current_user, id=id).first()

    if not bookmark:
        return jsonify({
            "message" : "Not  item found"
        }), HTTP_404_NOT_FOUND

    return jsonify({
            'id' : bookmark.id,
            'url' : bookmark.url,
            'short_url' : bookmark.short_url,
            'visit' : bookmark.visits,
            'body' : bookmark.body,
            'created_at' : bookmark.created_at,
            'updated_at' : bookmark.updated_at

            }), HTTP_200_OK


@bookmarks.put("/<int:id>")
@bookmarks.patch("/<int:id>")
@jwt_required()
def editbookmark(id):
    current_user = get_jwt_identity()

    bookmark = Bookmark.query.filter_by(user_id=current_user, id=id).first()

    if not bookmark:
        return jsonify({
            "message" : "Not  item found"
        }), HTTP_404_NOT_FOUND
    
    body = request.get_json().get('body', '')
    url = request.get_json().get('url', '')

    if not validators.url(url):
        return jsonify({
            'error' : 'Enter a valid url'
        }), HTTP_400_BAD_REQUEST
    

    bookmark.url=url
    bookmark.body=body

    db.session.commit()

    return jsonify({
            'id' : bookmark.id,
            'url' : bookmark.url,
            'short_url' : bookmark.short_url,
            'visit' : bookmark.visits,
            'body' : bookmark.body,
            'created_at' : bookmark.created_at,
            'updated_at' : bookmark.updated_at

            }), HTTP_200_OK


@bookmarks.delete("/<int:id>")
@jwt_required()
def deletebookmark(id):
    current_user = get_jwt_identity()

    bookmark = Bookmark.query.filter_by(user_id=current_user, id=id).first()

    if not bookmark:
        return jsonify({
            "message" : "Not  item found"
        }), HTTP_404_NOT_FOUND
    
    db.session.delete(bookmark)
    db.session.commit()

    return jsonify({}), HTTP_204_NO_CONTENT

@bookmarks.get("/stats")
@jwt_required()
@swag_from('./docs/bookmarks/stats.yaml')
def get_stats():
    current_user = get_jwt_identity()
    data = []
    items = Bookmark.query.filter_by(user_id=current_user).all()

    for item in items:
        new_link = {
            'visits': item.visits,
            'url' : item.url,
            'id' : item.id,
            'short_url' : item.short_url
        }
        data.append(new_link)

    return jsonify({'data' : data}), HTTP_200_OK