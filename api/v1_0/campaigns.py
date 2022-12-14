from crypt import methods
from flask import *
from db import Database, make_file
from handle_apikeys import *
from flask_login import current_user

db_campaigns = Database(make_file("data/db/campaigns.json"))

campaigns_api_v1 = Blueprint("campaigns_api_v1", __name__)


@campaigns_api_v1.route("/api/v1.0/campaigns/", methods=["GET"])
def get_campaigns():
    if not validate(request.args.get("apikey")):
        abort(403)
    return jsonify(db_campaigns.get_all()), 200


@campaigns_api_v1.route("/api/v1.0/campaigns/<int:key>/", methods=["GET"])
def get_campaign(key):
    if not validate(request.args.get("apikey")):
        abort(403)
    if db_campaigns.has_key(key):
        return db_campaigns.get_key(key), 200
    abort(404)


@campaigns_api_v1.route(
    "/api/v1.0/campaigns/<int:key>/", methods=["PUT"]
)  # TODO: This breaks the magicaltavern-bot. An API Version v1.1 has to be created which has @campaigns_api_v1.route("/api/v1.0/campaigns/<int:key>/player/", methods=["PUT"]) instead of the current PUT function.
def toggle_player(key):
    #   We update the player list and count by modifying an in-memory clone of the requested
    #   key-value-pair, and then updating the database when we are done. This saves disk activity.
    #   I think.
    if not validate(request.args.get("apikey")):
        abort(403)
    request_player = str(request.args.get("player"))
    campaign: dict = db_campaigns.get_key(key)
    print(str(campaign))
    campaign_players: list = campaign["players"]
    campaign_players_count: int = campaign["players_current"]
    if request_player in campaign_players:
        campaign_players.remove(request_player)
        campaign.update({"players": campaign_players})
        campaign.update({"players_current": campaign_players_count - 1})
        db_campaigns.set_key(campaign, key)
        return "True"
    else:
        if campaign_players_count + 1 > campaign["players_max"]:
            abort(409, description="Too many players in this campaign.")
        campaign_players.append(request_player)
        campaign.update({"players": campaign_players})
        campaign.update({"players_current": campaign_players_count + 1})
        db_campaigns.set_key(campaign, key)
        return "False"


@campaigns_api_v1.route("/api/v1.0/campaigns/<int:key>/has_view/", methods=["PUT"])
def confirm_view(key):
    #   We update the player list and count by modifying an in-memory clone of the requested
    #   key-value-pair, and then updating the database when we are done. This saves disk activity.
    #   I think.
    if not validate(request.args.get("apikey")):
        abort(403)
    campaign: dict = db_campaigns.get_key(key)
    if "has_view" in campaign.keys():
        campaign.update({"has_view": True})
        return jsonify(True)
    else:
        campaign.update({"has_view": False})
        return jsonify(False)


def toggle_player_web(key):
    # Another version is needed for the website logic (i think)
    campaign: dict = db_campaigns.get_key(key)
    campaign_players: list = campaign["players"]
    campaign_players_count: int = campaign["players_current"]

    # check if user is guest and the email should be used for identification
    if current_user.is_guest():
        request_player = current_user.email
    else:
        # may soon be used to have registered users sign in with username but not yet
        request_player = current_user.email

    if request_player in campaign_players:
        campaign_players.remove(request_player)
        campaign.update({"players": campaign_players})
        campaign.update({"players_current": campaign_players_count - 1})
    else:
        campaign_players.append(request_player)
        campaign.update({"players": campaign_players})
        campaign.update({"players_current": campaign_players_count + 1})
    return json.dumps(db_campaigns.set_key(campaign, key), indent=4)


@campaigns_api_v1.route("/api/v1.0/campaigns/", methods=["POST"])
def set_campaign():
    if not validate(request.args.get("apikey")):
        abort(403)
    key = request.args.get("id")
    data_required = {
        "name": request.json["name"],
        "dungeon_master": request.json["dungeon_master"],
        "description": request.json["description"],
        "players_min": request.json["players_min"],
        "players_max": request.json["players_max"],
        "complexity": request.json["complexity"],
        "place": request.json["place"],
        "time": request.json["time"],
        "content_warnings": request.json["content_warnings"],
        "ruleset": request.json["ruleset"],
        "campaign_length": request.json["campaign_length"],
        "language": request.json["language"],
        "character_creation": request.json["character_creation"],
        "briefing": request.json["briefing"],
        "notes": request.json["notes"],
    }
    if not request.json:
        abort(400)

    for key_required in data_required.keys():
        if key_required not in request.json:
            abort(400)

    data_optional_or_preset = {
        "image_url": request.json.get("image_url", ""),
        "players_current": 0,
        "players": [],
        "has_view": False,
    }

    return_value = db_campaigns.set_key((data_required | data_optional_or_preset), key)
    return jsonify(return_value)


@campaigns_api_v1.route("/api/v1.0/campaigns/dm/<int:id>/", methods=["GET"])
def get_where_dm(id):
    if not validate(request.args.get("apikey")):
        abort(403)
    campaigns_all = db_campaigns.get_all()
    campaigns_dm = []
    for key in campaigns_all.keys():
        if campaigns_all[key]["dungeon_master"] == id:
            campaigns_dm.append(key)
    return jsonify(campaigns_dm), 200
