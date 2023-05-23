import matplotlib.path as mplPath
import numpy as np
from shapely.geometry import Point, Polygon
import cv2
import pytesseract
from api.controller.text_functions import TextCorrections
import os


class OCR_plumping_bills:
    """this class will OCR plumbing document billing from image format like jpg or png"""
    def __init__(self, bills_path):
        self.bills_path = bills_path
        self.com_lo_path = None
        self.tab_crop_path = None

    def segment_bills(self):
        try:
            img_path = self.bills_path
            im_np = np.frombuffer(img_path, np.uint8)
            img = cv2.imdecode(im_np, cv2.IMREAD_COLOR)
            down_width = 1920
            down_height = 1080
            down_points = (down_width, down_height)
            resized_down = cv2.resize(img, down_points, interpolation= cv2.INTER_LINEAR)
            #base_image = img.copy()
            gray_img = cv2.cvtColor(resized_down,cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray_img,(5,5),0)
            thresh = cv2.threshold(blur,0,255,cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
            kernal = cv2.getStructuringElement(cv2.MORPH_RECT, (4,18))
            dilate = cv2.dilate(thresh, kernal, iterations=1)
            cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = cnts[0] if len(cnts) == 2 else cnts[1]
            cnts = sorted(cnts, key=lambda x: cv2.boundingRect(x)[0])

            a, b, c, d = 300, 170, 550, 80
            im1 = cv2.rectangle(resized_down, (a,b), (a+c, b+d), (36,255,12),2)
            cropped = im1[b:b + d, a:a + c+10]
            self.com_lo_path = "api/controller/ocr_plumping/p01crop_img/com_lo.jpeg"
            cv2.imwrite(self.com_lo_path,cropped)

            cop = 0
            for c in cnts:
                x, y, w, h = cv2.boundingRect(c)
                #table and total_amount
                if h > 400:
                    a, b, c, d = x, y, w, h 
                    cv2.rectangle(resized_down, (a,b), (a+c, b+d), (36,255,12),2)
                    cropped = resized_down[b:b + d+15, a:a + c]
                    self.tab_crop_path = "api/controller/ocr_plumping/p01crop_img/"+str(cop)+".jpeg"
                    cv2.imwrite(self.tab_crop_path,cropped)
                    cop+=1
        except Exception as e:
            print("An error occurred while processing the image: ", str(e))
    
    def ocr_price_date_con(self):
        """ocr from crop price, price+tax, read_date, account_no. and consumtions"""
        if self.tab_crop_path:
            crop_img = cv2.imread(self.tab_crop_path)
            crop_gray = cv2.cvtColor(crop_img,cv2.COLOR_BGR2GRAY)
            custom_config = r'--oem 3 --psm 4'
            crop_text = pytesseract.image_to_string(crop_gray, lang='tha+eng', config=custom_config)
            uncleaned_sections = crop_text.split('\n')
            sections = []
            for section in uncleaned_sections:
                sections.append(TextCorrections.clean_text(section.splitlines()))
            sec_list = list(filter(None, sections))
            acc_no = sec_list[0][0].split(' ')
            acc_no = list(filter(None, acc_no))
            acc_no = acc_no[1]
            sec_date = sec_list[3][0].split(' ')
            sec_date = list(filter(None, sec_date))
            before_date = sec_date[2]
            after_date = sec_date[0]
            consumtion = sec_date[-1]
            price = sec_list[-2][0].split(' ')
            price = list(filter(None, price))
            price = price[-1]
            price = TextCorrections.collect_float_format(price)
            tax = sec_list[-1][0].split(' ')
            tax = list(filter(None, tax))
            tax = tax[-1]
            tax = TextCorrections.collect_float_format(tax)
            amount = float(price.replace(',', ''))+float(tax.replace(',', ''))
            amount = TextCorrections.collect_float_format(str(amount))

            return [acc_no, before_date, after_date, consumtion, price, amount]
        else:
            return "tab_crop path not found"

    def ocr_comname_lo(self):
        """ocr from crop Company Name and Locations"""
        if self.com_lo_path: 
            crop_img = cv2.imread(self.com_lo_path)
            crop_gray = cv2.cvtColor(crop_img,cv2.COLOR_BGR2GRAY)
            custom_config = r'--oem 3 --psm 4'
            crop_text = pytesseract.image_to_string(crop_gray, lang='tha+eng', config=custom_config)
            uncleaned_sections = crop_text.split('\n')
            sections = []
            for section in uncleaned_sections:
                sections.append(TextCorrections.clean_text(section.splitlines()))
            sec_list = list(filter(None, sections))
            com_name = sec_list[0][0].split(' ')
            company_name = ' '.join(com_name[1:])
            com_lo = sec_list[-1][0].split(' ')
            locations = ' '.join(com_lo[1:])

            return [company_name, locations]
        else:
            return "com_lo path not found"


    


        