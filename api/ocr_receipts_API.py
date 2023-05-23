from flask import current_app
import spacy
from spacy.tokens import DocBin
from tqdm import tqdm
import shutil
import zipfile
import os
import pytesseract
from PIL import Image
import numpy as np
import cv2
import re
import json
from api.controller.TextCoverter import TextConverter
import time
import pandas as pd
import difflib

product_carbon_lookup = os.path.join(os.getcwd() + "/staticfiles/product_carbon_lookup.json")
file_sub_class_lookup = open(product_carbon_lookup, encoding="utf8")
product_data = json.load(file_sub_class_lookup)
barcode_list = []
for product in product_data['product']:
    barcode_list.append(product['barcode'])


class OCR_receipts_API:
    def __init__(self, format_id, image_path, model_logo, model_rep_detect):
        self.format_id = format_id
        self.image_path = image_path
        self.model_logo = model_logo
        self.model_rep_detect = model_rep_detect
        self.barcode_list = barcode_list

    def ocr_receipts(self):
        start_time = time.time()
        print("pytesseract version: ", pytesseract.get_tesseract_version())
        if self.format_id == 're00':
            img_path = self.image_path
            im_np = np.frombuffer(img_path, np.uint8)
            img = cv2.imdecode(im_np, cv2.IMREAD_COLOR)
            text = pytesseract.image_to_string(img, lang='eng', config='--oem 3 --psm 4')
            nlp = spacy.load("api/model/model-best")
            doc = nlp(text)
            receipt_info = {'TAX_ID': [],
                            'TAX_INV': [],
                            'POS_ID': [],
                            'DATE': [],
                            'TIME': [],
                            'SUB_TOTALS': [],
                            'TOTALS': [],
                            'CASH': [],
                            'CHANGE': []}
            for ent in doc.ents:
                if ent.label_ in receipt_info:
                    receipt_info[ent.label_].append(ent.text)
            end_time = time.time()
            elapsed_time = end_time - start_time
            print("Elapsed time: {:.2f} seconds".format(elapsed_time))
            return receipt_info
        elif self.format_id == 'cero01':
            start_time = time.time()
            model_rep_detect = self.model_rep_detect
            img_path = self.image_path
            im_np = np.frombuffer(img_path, np.uint8)
            img = cv2.imdecode(im_np, cv2.IMREAD_COLOR)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # cv2.imwrite('cropped_img0.png', img)
            try:
                res = model_rep_detect(img, imgsz=640, conf=0.7)
                box = res[0].boxes.data
                box_data = box.cpu().numpy()[0][:4]
                x1, y1, x2, y2 = int(box_data[0]), int(box_data[1]), int(box_data[2]), int(box_data[3])
                cropped_img = gray[y1:y2, x1:x2]
                croped_img_rgb = img[y1:y2, x1:x2]
                width = 720
                height = int(cropped_img.shape[0] * (width / cropped_img.shape[1]))
                dim = (width, height)
                cropped_img = cv2.resize(cropped_img, dim, interpolation=cv2.INTER_AREA)
                croped_img_rgb = cv2.resize(croped_img_rgb, dim, interpolation=cv2.INTER_AREA)
                k1 = np.ones((1, 2), np.uint8)
                erosion = cv2.erode(cropped_img, k1, iterations = 1)
                print("Receipts Detected")
            except:
                return "Receipts not detect please try again."
            end_time = time.time()
            elapsed_time = end_time - start_time
            print("111 Elapsed time of Image Preprocess: {:.2f} seconds".format(time.time() - start_time))
            try:
                model_logo = self.model_logo
                results = model_logo(croped_img_rgb, imgsz=640, conf=0.25)
                logo_detect = results[0].names[0]
                conf_data = results[0].boxes.data
                conf = conf_data[0][4].cpu().numpy()
                print("logo conf: ", conf)
            except:
                logo_detect = 'unknown'
            print("222 Elapsed time of Image Preprocess: {:.2f} seconds".format(time.time() - start_time))
            # return "Invalid Receipts"
            custom_config = r"--oem 3 --psm 6 --dpi 600 -c tessedit_char_blacklist=©‘‘;+°&\'\""
            text = pytesseract.image_to_string(erosion,lang="eng", config=custom_config)
            print("333 Elapsed time of Image Preprocess: {:.2f} seconds".format(time.time() - start_time))
            # nlp = spacy.load("api/model/new_model-best")
            nlp = current_app.config['cero03_nlp']
            doc = nlp(text)
            receipt_info2 = {'TAX_INV_ID': [],
                            'PROD_ID': [],
                            'DATE_TIME':[],
                            'MEMBER_ID':[],
                            'MEMBER_NAME':[],
                            'PAY_METHOD':[]
                                }
            for ent in doc.ents:
                if ent.label_ in receipt_info2:
                    receipt_info2[ent.label_].append(ent.text)
            prod_id = receipt_info2['PROD_ID']
            tax_id = []
            tax_inv_id = receipt_info2['TAX_INV_ID']
            if tax_inv_id:
                delimiters = [',', '.']
                for i in tax_inv_id:
                    split_text = re.split('|'.join(map(re.escape, delimiters)), i)
                    tax_num = split_text[-1].replace(' ', '')
                    con_text = TextConverter().convert_text(tax_num)
                    if con_text.isdigit():
                        tax_id.append(con_text)
                    else:
                        tax_id.append('unknown')
            else:
                tax_id.append('unknown')
            prod_list = []
            other_prod = []
            print(prod_id)
            for i in prod_id:
                stripped_text = i.replace(' ', '')
                if len(stripped_text) == 13:
                    con_text = TextConverter().convert_text(stripped_text)
                    print("context: ",con_text)
                    con_text = '885'+con_text[3:]
                    for barcode in barcode_list:
                        similarity_score = difflib.SequenceMatcher(None, con_text, str(barcode)).ratio()
                        if similarity_score > 0.92:
                            print('len 13: ',con_text)
                            print(similarity_score)
                            prod_list.append(str(barcode))
                        else:
                            pass
                elif len(stripped_text) == 14:
                    con_text = TextConverter().convert_text(stripped_text)
                    print("len 14 context: ",con_text)
                    pro_id = con_text[1:]
                    pro_id= '885'+pro_id[3:]
                    for barcode in barcode_list:
                        similarity_score = difflib.SequenceMatcher(None, pro_id, str(barcode)).ratio()
                        if similarity_score > 0.92:
                            print(pro_id)
                            print(similarity_score)
                            prod_list.append(str(barcode))
                        else:
                            pass 
                else:
                    con_text = TextConverter().convert_text(stripped_text)
                    print(con_text)
                    other_prod.append(con_text)
            print(prod_list)
            print(other_prod)
            prod_json_list = []
            other_json_list = []
            for product in product_data['product']:
                for prod_id in prod_list:
                    if str(product['barcode']) == prod_id:
                        pro_data = {"barcode": prod_id, 
                        "cero_earn": product["cero_earn"],
                        "saved_carbon":product["saved_carbon"],
                        "saving_units":product["saving_units"],
                        "label_type":product["label_type"]
                        }
                        prod_json_list.append(pro_data)
            for product in product_data['product']:
                for prod_id in other_prod:
                    if str(product['barcode']) == prod_id:
                        pro_data = {"barcode": prod_id, 
                        "cero_earn": product["cero_earn"],
                        "saved_carbon":product["saved_carbon"],
                        "saving_units":product["saving_units"],
                        "label_type":product["label_type"]
                        }
                        other_json_list.append(pro_data)
            date_time = receipt_info2['DATE_TIME']
            print('date detect ',date_time )
            if date_time:
                date_time = date_time[-1].split()
                print('list',date_time)
                if len(date_time) > 1:
                    date = date_time[0]
                    print(date)
                    dtime = date_time[1]
                    print(dtime)
                    if len(dtime) != 5:
                        dtime = 'unknown'
                    date = date[0:2]+'/'+date[3:5]+'/'+date[6:]
                    print(date)
                    date = TextConverter().correct_date_format(date)
                else:
                    date = date_time[0]
                    dtime = 'unknown'
                    date = date[0:2]+'/'+date[3:5]+'/'+date[6:]
                    date = TextConverter().correct_date_format(date)
            else:
                print('not in loop')
                date = 'unknown'
                dtime = 'unknown'
            member_id = receipt_info2['MEMBER_ID']
            if member_id:
                member_id = member_id[0]
            else:
                member_id = 'unknown'
            member_name = receipt_info2['MEMBER_NAME']
            if member_name:
                member_name = member_name[0]
            else:
                member_name = 'unknown'
            pay_method = receipt_info2['PAY_METHOD']
            if pay_method:
                pay_method = pay_method[0]
            else:
                pay_method = 'unknown'
            result = {"status": 'success',
                      "market": logo_detect,
                      "date": date,
                      "time": dtime,
                      "member_id": member_id,
                      "member_name": member_name,
                      "pay_method": pay_method,
                      "tax_inv_id": tax_id[0],
                      "prod_list": prod_json_list,
                      "other_prod": other_json_list}
            end_time = time.time()
            elapsed_time = end_time - start_time
            print("--- End Elapsed time: {:.2f} seconds ---".format(time.time() - start_time))
            return result
        else:
            return "Format ID invalid"
