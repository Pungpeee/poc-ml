import werkzeug
from flask import Flask
from flask_restful import Resource, Api, reqparse, abort
import os
from api.ocr_electricity_API import OCR_electricity_bills_API
from api.ocr_plumping_API import OCR_plumping_bills_API
from api.ocr_receipts_API import OCR_receipts_API
from api.controller.dbProcess import addData
from flask_httpauth import HTTPBasicAuth
from dotenv import load_dotenv
import base64
from api.controller.upload_image import Img2blob

load_dotenv()
auth = HTTPBasicAuth()


@auth.get_password
def get_password(username):
    if username == os.environ.get('ADMIN_USERNAME'):
        return os.environ.get('ADMIN_PASSWORD')
    return None


@auth.error_handler
def unauthorized():
    return {'error': 'Unauthorized access'}, 401


class Router_ocr_api(Resource):
    def __init__(self, model_logo, model_rep_detect):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument(
            "format_type",
            location="form",
            required=True,
            help="Please add format_type"
        )
        self.parser.add_argument(
            "format_id",
            location="form",
            required=True,
            help="Please add format_id"
        )
        self.parser.add_argument(
            "image_file",
            type=werkzeug.datastructures.FileStorage,
            location="files",
            required=True,
            help="Please add image_path"
        )
        self.model_logo = model_logo
        self.model_rep_detect = model_rep_detect

    @auth.login_required
    def post(self):
        args = self.parser.parse_args()
        format_type = args['format_type']
        format_id = args['format_id']
        image_path = args['image_file'].read()
        model_logo = self.model_logo
        model_rep_detect = self.model_rep_detect
        if format_type == 'electricity_bills':
            ocr_electricity_bills = OCR_electricity_bills_API(
                format_id, image_path)
            result = ocr_electricity_bills.ocr_electricity_bills()
            base64_data = base64.b64encode(image_path).decode('ascii')
            log_data = {'log': result,
                        'format_type': format_type,
                        'format_id': format_id,
                        'url_img': base64_data}
            # db process
            # save log to db
            addData(log_data).insertToDB()
            # # clear crop image
            folder = os.path.join(
                os.getcwd() + '/api/controller/ocr_electricity/' + format_id + 'crop_img')
            for file in os.listdir(folder):
                # check if file is an image
                if file.endswith('.jpg') or file.endswith('.png') or file.endswith('.jpeg'):
                    # delete the file
                    os.remove(os.path.join(folder, file))
            print("OCR Process Successed")
            return result
        elif format_type == 'plumping_bills':
            ocr_plumping_bills = OCR_plumping_bills_API(
                format_id, image_path)
            result = ocr_plumping_bills.ocr_plumbing_bills()
            print("OCR Process Successed")
            base64_data = base64.b64encode(image_path).decode('ascii')
            log_data = {'log': result,
                        'format_type': format_type,
                        'format_id': format_id,
                        'url_img': base64_data}
            # db process
            # save log to db
            addData(log_data).insertToDB()
            # # clear crop image
            folder = os.path.join(
                os.getcwd() + "/api/controller/ocr_plumping/" + format_id + 'crop_img')
            for file in os.listdir(folder):
                # check if file is an image
                if file.endswith('.jpg') or file.endswith('.png') or file.endswith('.jpeg'):
                    # delete the file
                    os.remove(os.path.join(folder, file))
            print(result)
            return result
        elif format_type == 'receipts':
            ocr_receipts = OCR_receipts_API(format_id, image_path, model_logo, model_rep_detect)
            result = ocr_receipts.ocr_receipts()
            print("OCR Process Successed")
            base64_data = base64.b64encode(image_path).decode('ascii')
            img_url = Img2blob(base64_data).upload_img2blob()
            log_data = {'log': result,
                        'format_type': format_type,
                        'format_id': format_id,
                        'url_img': img_url}
            # db process
            # save log to db
            addData(log_data).insertToDB()
            print(log_data)
            return result
        else:
            return 'Error'

    def get(self):
        return 'get success'
