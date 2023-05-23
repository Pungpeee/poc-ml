from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import base64
from dotenv import load_dotenv
import os
from datetime import datetime
import uuid


load_dotenv()
class Img2blob():
    def __init__(self,base64_data):
        # Set the connection string and container name
        self.connection_string = os.environ.get('SAS_TOKEN')
        self.container_name = os.environ.get('CON_IMG_NAME')
        self.base64_data = base64_data
    def upload_img2blob(self):
        # Decode the Base64 data to binary
        binary_data = base64.b64decode(self.base64_data)
        # Create a BlobServiceClient object
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        # Create a ContainerClient object
        container_client = blob_service_client.get_container_client(self.container_name)
        # Set the prefix for the blob name
        prefix = "cero_"
        # Generate a unique identifier
        unique_id = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f") + "_" + str(uuid.uuid4())
        # Create the blob name by concatenating the prefix and unique identifier
        blob_name = prefix + unique_id + ".jpg"
        # Create a BlobClient object with the generated blob name
        blob_client = container_client.get_blob_client(blob_name)
        # Upload the image data to the blob
        blob_client.upload_blob(binary_data)
        #get image url from blob
        blob_client = blob_service_client.get_blob_client(self.container_name, blob_name)
        img_url = blob_client.url
        return img_url

