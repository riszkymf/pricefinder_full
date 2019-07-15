from flask import Blueprint
from flask_restful import Api
from .company import *
from .product_company import *
from .product import *
from .vm import *
from .additional_features import *
from .worker import *
from .hosting import *
from .config import *

api_blueprint = Blueprint("api",__name__,url_prefix="/api")
api = Api(api_blueprint)
api.add_resource(CompanyDetails, '/company')
api.add_resource(ProductDetails, '/product')
api.add_resource(CompanyProducts,'/company_product')
api.add_resource(VMDetails,'/vm')
api.add_resource(WorkerDetails,'/worker')
api.add_resource(HostingDetails,'/hosting')
api.add_resource(FeatureDetails,'/additional_features')
api.add_resource(ConfigCrawler,'/config')