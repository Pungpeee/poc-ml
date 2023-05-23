from flask_marshmallow import Schema
from marshmallow.fields import Str, Dict


class OCR_ml_Schema(Schema):
    class Meta:
        # Fields to expose
        fields = ["data", "status"]

    message = Dict()
