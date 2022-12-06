from flask import Blueprint, jsonify
from flask_restful.reqparse import RequestParser
from .vars import *
import requests

views = Blueprint("views", __name__)


@views.route("/top/<int:post_id>", methods=["GET"])
@views.route("/top", methods=["GET"])
def get_top_posts(post_id=None):
    try:
        comments = requests.get(COMMENTS).json()
        comment_post_id = [i.get("postId", 0) for i in comments]
        if post_id:
            all_posts = [requests.get(f"{POSTS}/{post_id}").json()]
        else:
            all_posts = requests.get(POSTS).json()
        for post in all_posts:
            post["total_number_of_comments"] = comment_post_id.count(post["id"])
            # rename keys
            post["post_id"] = post.pop("id")
            post["post_title"] = post.pop("title")
            post["post_body"] = post.pop("body")
        all_posts_sorted = sorted(all_posts, key=lambda x: x["total_number_of_comments"])
        return all_posts_sorted, 200
        # return jsonify({"res": True, "out": comments.json()}), 200
    except Exception as e:
        return jsonify({"res": False, "msg": str(e)}), 400


@views.route("/filter", methods=["GET"])
def filter_comments():
    try:
        parser = RequestParser()
        # comment
        parser.add_argument("postId", type=int)
        parser.add_argument("id", type=int)
        parser.add_argument("name", type=str)
        parser.add_argument("email", type=str)
        parser.add_argument("body", type=str)

        json_out = parser.parse_args()

        try:
            assert isinstance(json_out["postId"], int) or json_out["postId"] is None, \
                "post ID must be of type int"
            assert isinstance(json_out["id"], int) or json_out["id"] is None, \
                "ID must be of type int"
            assert isinstance(json_out["name"], str) or json_out["name"] is None, \
                "name must be of type str"
            assert isinstance(json_out["email"], str) or json_out["email"] is None, \
                "email must be of type str"
            assert isinstance(json_out["body"], str) or json_out["body"] is None, \
                "body must be of type str"
        except AssertionError as e:
            return jsonify({"res": False, "msg": str(e)}), 400

        # remove None values
        json_out = {i: json_out[i] for i in json_out if json_out[i]}

        comments = requests.get(COMMENTS).json()

        for key in json_out:
            if key in ["name", "email", "body"]:  # perform string matching
                comments = [c for c in comments if json_out[key].lower() in c[key].lower()]
            else:  # perform exact matching
                comments = [c for c in comments if json_out[key] == c[key]]

        return comments, 200
    except Exception as e:
        return jsonify({"res": False, "msg": str(e)}), 400
