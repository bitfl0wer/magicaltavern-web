from flask import Blueprint, request, jsonify
from api.v2_0.authentication import abort_if_token_invalid
from api.v2_0.models import table_to_dict, Campaign

campaigns_api_v2 = Blueprint("campaigns_api_v2", __name__)


@campaigns_api_v2.route("/api/v2.0/campaigns/", methods=["GET"])
def get_all_campaigns():
    abort_if_token_invalid(request)
    return jsonify(table_to_dict(Campaign)), 200
