from flask import Blueprint
from flask_restful import Api
from .product import *
from .activeuser import *

api_blueprint = Blueprint("api", __name__, url_prefix='/api')
api = Api(api_blueprint)

api.add_resource(Analytics, "/analytics/<product_name>")
api.add_resource(AnalyticsAll,"/analytics")
api.add_resource(ActiveUsers, "/active_users/<product_name>")
api.add_resource(ActiveUsersAll,"/active_users")
