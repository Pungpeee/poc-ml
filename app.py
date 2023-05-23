import os
from flask import Flask
from flask_restful import Api
from api.router_api import Router_ocr_api
from api.barcode_API import Barcode_api
#import torch
import pandas as pd
import spacy
import json
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
from ultralytics import YOLO

load_dotenv()



def create_app():
    app = Flask(__name__)

    @app.route('/', methods=['GET'])
    def health_check():
        return 'OK', 200
    
    return app


if __name__ == "__main__":
    container_name =os.getenv("CONTAINER_NAME")
    temp_folder1 = os.path.join(os.getcwd() + '/api/model/newlest_model-best')
    model_prefix1 = 'newlest_model-best/'
    # Create a BlobServiceClient and get the container and blob clients
    connection_string = os.getenv("SAS_TOKEN")
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    # List the blobs in the container that match the model prefix 1
    blobs = container_client.list_blobs(name_starts_with=model_prefix1)
    # Download each blob to the appropriate directory
    local_model_dir = os.path.join(os.getcwd(), temp_folder1)
    for blob in blobs:
        # Create the local directory if it does not exist
        local_blob_dir = os.path.join(local_model_dir, os.path.dirname(blob.name[len(model_prefix1):]))
        os.makedirs(local_blob_dir, exist_ok=True)
        # Download the blob to the local directory
        blob_client = container_client.get_blob_client(blob.name)
        local_blob_path = os.path.join(local_blob_dir, os.path.basename(blob.name))
        with open(local_blob_path, "wb") as f:
            download_stream = blob_client.download_blob()
            f.write(download_stream.readall())
    print('download all model from AZURE Blob Complete')

    os.environ['OMP_THREAD_LIMIT'] = '1'
    from argparse import ArgumentParser
    prefix = "/ocr-ml"

    # torch.hub._validate_not_a_forked_repo = lambda a, b, c: True
    model_logo_path = os.path.join(os.getcwd() + "/weights/logo_yolo8.pt")
    model_rep_detect_path = os.path.join(os.getcwd() + "/weights/receipts_detectv1.pt")
    # model_logo = torch.hub.load(
    #     "ultralytics/yolov5",
    #     "custom",
    #     path=model_logo_path,
    #     force_reload=True,
    #     trust_repo=True,
    # )
    
    # Load a model yoloV8
    model_logo = YOLO(model_logo_path)
    print("Load logo_model success")

    model_rep_detect = YOLO(model_rep_detect_path)
    print("Load receipt_detection_model success")

    parser = ArgumentParser()
    parser.add_argument(
        "-p", "--port", default=5000, type=int, help="port to listen on"
    )
    args = parser.parse_args()
    print(args)
    port = args.port

    app = create_app()
    api = Api(app)
    api.add_resource(Router_ocr_api, prefix + "/v1/ml/ocr-ml",
                     resource_class_kwargs={
                         "model_logo": model_logo,
                         "model_rep_detect": model_rep_detect
                     })
    api.add_resource(Barcode_api, prefix + "/v1/ml/barcode-ml")

    # preload model
    app.config['cero03_nlp'] = spacy.load(os.path.join(os.getcwd() +"/api/model/newlest_model-best"))
    #app.run(debug=True)
    print(port)
    app.run(host="0.0.0.0", port=port)
