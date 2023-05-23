import werkzeug
from flask import Flask
from flask_restful import Resource, Api, reqparse, abort
import os
from api.controller.dbProcess import addData
from flask_httpauth import HTTPBasicAuth
from dotenv import load_dotenv
import json
from azure.storage.blob import BlobServiceClient

load_dotenv()
auth = HTTPBasicAuth()

product_carbon_lookup = os.path.join(os.getcwd() + "/staticfiles/product_carbon_lookup.json")
file_sub_class_lookup = open(product_carbon_lookup, encoding="utf8")
product_data = json.load(file_sub_class_lookup)
# Initialize BlobServiceClient with your connection string
connection_string = os.getenv("SAS_TOKEN")
blob_service_client = BlobServiceClient.from_connection_string(connection_string)
container_name = "vekocrmliamges"





@auth.get_password
def get_password(username):
    if username == os.environ.get('ADMIN_USERNAME'):
        return os.environ.get('ADMIN_PASSWORD')
    return None


@auth.error_handler
def unauthorized():
    return {'error': 'Unauthorized access'}, 401

class Barcode_api(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument(
            "format_type",
            location="form",
            required=True,
            help="Please add format_type"
        )
        self.parser.add_argument(
            "barcode_id",
            location="form",
            required=True,
            help="Please add barcode_id"
        )

    @auth.login_required
    def post(self):
        args = self.parser.parse_args()
        format_type = args['format_type']
        barcode_id = args['barcode_id']
        res = None
        if format_type == 'barcode':
            for product in product_data['product']:
                if product['barcode'] == barcode_id:
                    res = product
                else:
                    pass        
            if res is None:
                return "Not Found Product"
        blob_name = str(res['barcode'])+'.jpg'
        blob_client = blob_service_client.get_blob_client(container_name, blob_name)
        image_url = blob_client.url
        res["product_img_url"] = image_url
        # db process
        log_data = res
        # save log to db
        addData(log_data).insertToDB()
        print(res)
        return res                
            
