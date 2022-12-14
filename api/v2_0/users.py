import bleach
from flask import Blueprint, request, jsonify, abort, escape
from api.v2_0.authentication import abort_if_token_invalid
from api.v2_0.models import (
    User,
    ensure_player_exists,
    table_to_dict,
    does_campaign_exist,
    campaign_player_association,
    campaign_dm_association,
    Campaign,
    ACCESS,
)
from api.v2_0.models import dbsql as db

users = Blueprint("users", __name__)


@users.route("/api/v2.0/users/", methods=["GET"])
def get_all_users():
    abort_if_token_invalid(request)
    users = table_to_dict(User)
    return jsonify(users)


@users.route("/api/v2.0/users/<int:id>/", methods=["GET"])
def get_singular_user(id):
    abort_if_token_invalid(request)
    item = User.query.filter(User.id == id).one_or_none()
    if not item:
        abort(400, "This User does not exist.")
    item = item.to_dict()
    return jsonify(item), 200


@users.route("/api/v2.0/users/<int:user_id>/plays_campaigns/", methods=["GET"])
def get_campaigns_where_player(user_id):
    abort_if_token_invalid(request)
    items = (
        Campaign.query.join(campaign_player_association)
        .filter((campaign_player_association.c.player == user_id))
        .all()
    )

    if not items:
        return (jsonify({})), 200
    returned_dict = {}
    for item in items:
        returned_dict[item.id] = item.to_dict()

    return jsonify(returned_dict), 200


@users.route("/api/v2.0/users/<int:user_id>/dms_campaigns/", methods=["GET"])
def get_campaigns_where_dm(user_id):
    abort_if_token_invalid(request)
    items = (
        Campaign.query.join(campaign_dm_association)
        .filter((campaign_dm_association.c.dm == user_id))
        .all()
    )

    if not items:
        return (jsonify({})), 200
    returned_dict = {}
    for item in items:
        returned_dict[item.id] = item.to_dict()

    return jsonify(returned_dict), 200


@users.route(
    "/api/v2.0/users/<int:user_id>/modify_access/<int:access_level>/", methods=["PUT"]
)
def update_access_level(user_id, access_level):
    abort_if_token_invalid(request)
    if int(escape(access_level)) not in ACCESS.values():
        abort(
            400, "Invalid Access Level. Valid access values are integers from 0 to 3."
        )
    user = ensure_player_exists(escape(user_id))
    user.access = access_level
    db.session.commit()
    return (jsonify("Success.")), 200
