import matplotlib.path as mplPath
import numpy as np
from shapely.geometry import Point, Polygon
import cv2
import pytesseract
from api.controller.text_functions import TextCorrections
import os
import re
from PIL import Image
import io

class OCR_electricity_bills_segment01:
    """this class will OCR electricity document billing from image format like jpg or png"""
    def __init__(self,bills_path):
        self.bills_path = bills_path
        self.crop_path = None
    
    def segment_bills(self):
        img_path = self.bills_path
        im_np = np.frombuffer(img_path, np.uint8)
        img = cv2.imdecode(im_np, cv2.IMREAD_COLOR)
        down_width = 1920
        down_height = 1200
        down_points = (down_width, down_height)
        resized_down = cv2.resize(img, down_points, interpolation= cv2.INTER_LINEAR)
        #base_image = resized_down.copy()
        gray_img = cv2.cvtColor(resized_down,cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray_img,(5,5),0)
        thresh = cv2.threshold(blur,0,255,cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        kernal = cv2.getStructuringElement(cv2.MORPH_RECT, (3,13))
        dilate = cv2.dilate(thresh, kernal, iterations=1)
        cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        cnts = sorted(cnts, key=lambda x: cv2.boundingRect(x)[0])
        #crop focus point
        crop_number=0
        focus_point = [(703,299), (1160,440), (1233,440), (1675,250)]
        for c in cnts:
            x, y, w, h = cv2.boundingRect(c)
            poly_path = mplPath.Path(np.array([[x, y],
                                    [x, y+h],
                                    [x+w, y+h],
                                    [x+w, h]]))
            if poly_path.contains_point(focus_point[0]) == True and h > 120:
                cv2.rectangle(resized_down, (x,y), (x+w, y+h), (36,255,12),2)
                cropped = resized_down[y:y + h, x:x + w]
                self.crop_path = "api/controller/ocr_electricity/01crop_img/01crop"+str(crop_number)+".jpg"
                cv2.imwrite(self.crop_path,cropped)
                print(crop_number)
                crop_number+=1
            elif poly_path.contains_point(focus_point[1]) == True and w < 80 and h > 80:
                a, b, c, d = x-10, y-10, w+20, h+20 
                cv2.rectangle(resized_down, (a,b), (a+c, b+d), (36,255,12),2)
                cropped = resized_down[b:b + d, a:a + c]
                self.crop_path = "api/controller/ocr_electricity/01crop_img/01crop"+str(crop_number)+".jpg"
                cv2.imwrite(self.crop_path,cropped)
                print(crop_number)
                crop_number+=1
            elif poly_path.contains_point(focus_point[2]) == True and w < 80 and h > 80:
                a, b, c, d = x-10, y-10, w+20, h+20 
                cv2.rectangle(resized_down, (a,b), (a+c, b+d), (36,255,12),2)
                cropped = resized_down[b:b + d, a:a + c]
                self.crop_path = "api/controller/ocr_electricity/01crop_img/01crop"+str(crop_number)+".jpg"
                cv2.imwrite(self.crop_path,cropped)
                print(crop_number)
                crop_number+=1
            elif poly_path.contains_point(focus_point[3]) == True and h > 55:
                cv2.rectangle(resized_down, (x,y), (x+w, y+h), (36,255,12),2)
                cropped = resized_down[y:y + h, x:x + w]
                self.crop_path = "api/controller/ocr_electricity/01crop_img/01crop"+str(crop_number)+".jpg"
                cv2.imwrite(self.crop_path,cropped)
                print(crop_number)
                crop_number+=1
            else:
                pass

class OCR_electricity_bills01:
    def __init__(self,folder):
        self.folder = folder
        crop_list = []
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            crop_list.append(file_path)
        self.crop_list = crop_list

    def find_amount(img_path):
        img = str(img_path)
        #electric_amount
        amount_text = pytesseract.image_to_string(Image.open(img), lang='tha+eng')
        uncleaned_sections = amount_text.split('\n')
        sections = []
        for section in uncleaned_sections:
            sections.append(TextCorrections.clean_text(section.splitlines()))
        sec_list = list(filter(None, sections))
        text_totals_price = re.findall(r'[0-9]*', sec_list[-4][0]) #total before vax
        text_amount = re.findall(r'[0-9]*', sec_list[-1][0]) #Amount(totals+vax7%)
        totals_price = list(filter(None, text_totals_price))
        amount = list(filter(None, text_amount))
        sum_totals_price = TextCorrections.collect_num(totals_price)
        sum_amount = TextCorrections.collect_num(amount)
        return [sum_totals_price, sum_amount]
    
    def find_header(img_path):
        #meter_reader
        meter_img = str(img_path)
        meter_text = pytesseract.image_to_string(Image.open(meter_img), lang='tha+eng')
        uncleaned_sections = meter_text.split('\n')
        sections = []
        for section in uncleaned_sections:
            sections.append(TextCorrections.clean_text(section.splitlines()))
        sec_list = list(filter(None, sections))
      
        #meter_value
        regex_line = sec_list[-1][0].split(' ')
        meter_list = list(filter(None, regex_line))
        meter_read_date = meter_list[1]
        kWh = TextCorrections.collect_num2int(meter_list[4])

        #company_name
        name_line = sec_list[3][0].split(') ')
        name_list = list(filter(None, name_line))
        company_name = name_list[1].replace(' ', '')

        #company_address
        add_line = sec_list[4][0].split(') ')
        add_list = list(filter(None, add_line))
        company_address = add_list[1]

        return [meter_read_date, kWh, company_name, company_address]

    def find_unit_peak(img1,img2):
        unit_name_img = img1
        unit_value_img = img2
        unit_name_text = pytesseract.image_to_string(Image.open(unit_name_img), lang='tha+eng').replace(' ', '')
        unit_values_text = pytesseract.image_to_string(Image.open(unit_value_img), lang='eng').replace(' ', '')
        uncleaned_sections1 = unit_name_text.split('\n')
        uncleaned_sections2 = unit_values_text.split('\n')
        sections1 = []
        sections2 = []
        for section in uncleaned_sections1:
            sections1.append(TextCorrections.clean_text(section.splitlines()))
        sec_list1 = list(filter(None, sections1))
      
        for section in uncleaned_sections2:
            sections2.append(TextCorrections.clean_text(section.splitlines()))
        sec_list2 = list(filter(None, sections2))

        peak_list = []
        if len(sec_list1) == len(sec_list2):
            for i in range(len(sec_list1)):
                  peak = sec_list2[i][0]
                  peak_list.append(peak)
        return peak_list
    
    def find_installID(install_img):
        installation_img = install_img
        inid_text = pytesseract.image_to_string(Image.open(installation_img), lang='eng+tha')
        uncleaned_sections = inid_text.split('\n')
        sections = []
        for section in uncleaned_sections:
            sections.append(TextCorrections.clean_text(section.splitlines()))
        sec_list = list(filter(None, sections))
        install_id = sec_list[-1][0]
        return install_id

class OCR_electricity_bills_segment02:
    """this class will OCR electricity document billing from image format like jpg or png"""
    def __init__(self,bills_path):
        self.bills_path = bills_path
        self.crop_path = None
    def segment_bills(self):
        img_path = self.bills_path
        im_np = np.frombuffer(img_path, np.uint8)
        img = cv2.imdecode(im_np, cv2.IMREAD_COLOR) 
        down_width = 1080
        down_height = 1920
        down_points = (down_width, down_height)
        resized_down = cv2.resize(img, down_points, interpolation= cv2.INTER_LINEAR)
        #base_image = img.copy()
        gray_img = cv2.cvtColor(resized_down,cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray_img,(5,5),0)
        thresh = cv2.threshold(blur,0,255,cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        kernal = cv2.getStructuringElement(cv2.MORPH_RECT, (3,13))
        dilate = cv2.dilate(thresh, kernal, iterations=1)
        cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        cnts = sorted(cnts, key=lambda x: cv2.boundingRect(x)[0])
        #focus point
        focus_point = [(346,612), (525,804), (187,1483), (901,1328)]

        for c in cnts:
            x, y, w, h = cv2.boundingRect(c)
            poly_path = mplPath.Path(np.array([[x, y],
                                          [x, y+h],
                                    [x+w, y+h],
                                    [x+w, h]]))
            if poly_path.contains_point(focus_point[0]) == True and h < 100 and w < 130:
              a, b, c, d = x-5, y-5, w+210, h+15
              cv2.rectangle(resized_down, (a,b), (a+c, b+d), (36,255,12),2)
              cropped = resized_down[b:b + d, a:a + c]
              self.crop_path = "api/controller/ocr_electricity/e02crop_img/comname.jpg"
              cv2.imwrite(self.crop_path,cropped)
            elif poly_path.contains_point(focus_point[1]) == True and h > 170 and w > 220:
              cv2.rectangle(resized_down, (x,y), (x+w, y+h), (36,255,12),2)
              cropped = resized_down[y:y + h, x:x + w]
              self.crop_path = "api/controller/ocr_electricity/e02crop_img/table.jpg"
              cv2.imwrite(self.crop_path,cropped)
            elif poly_path.contains_point(focus_point[2]) == True and h > 170 and w > 220:
              cv2.rectangle(resized_down, (x,y), (x+w, y+h), (36,255,12),2)
              cropped = resized_down[y:y + h, x:x + w]
              self.crop_path = "api/controller/ocr_electricity/e02crop_img/table2.jpg"
              cv2.imwrite(self.crop_path,cropped)
            elif poly_path.contains_point(focus_point[3]) == True and h in range(60,130) and w in range(50,60):
              a, b, c, d = x-15, y, w+20, h
              cv2.rectangle(resized_down, (a,b), (a+c, b+d), (36,255,12),2)
              cropped = resized_down[b:b + d, a:a + c]
              self.crop_path = "api/controller/ocr_electricity/e02crop_img/peak.jpg"
              cv2.imwrite(self.crop_path,cropped)
            else:
              pass

class OCR_electricity_bills02:
    def cname_location(img_path):
        com_lo_img = img_path
        com_lo_text = pytesseract.image_to_string(Image.open(com_lo_img), lang='tha+eng')
        uncleaned_sections = com_lo_text.split('\n')
        sections = []
        for section in uncleaned_sections:
                  sections.append(TextCorrections.clean_text(section.splitlines()))
        sec_list = list(filter(None, sections))
        return [sec_list[0][0], sec_list[1][0]]
    
    def ocr_tables(img_path):
        table_img = img_path
        table_text = pytesseract.image_to_string(Image.open(table_img), lang='tha+eng')
        uncleaned_sections = table_text.split('\n')
        sections = []
        for section in uncleaned_sections:
                  sections.append(TextCorrections.clean_text(section.splitlines()))
        sec_list = list(filter(None, sections))
        sec01 = sec_list[1][0].split(' ')
        sec01 = list(filter(None, sec01))
        sec03 = sec_list[3][0].split(' ')
        sec03 = list(filter(None, sec03))
        installation_id = sec01[1]
        month = sec01[-1]
        meter_read_date = sec03[1]
        used_power_units = TextCorrections.collect_int_format(sec03[-2])
        return [installation_id, month, meter_read_date, used_power_units]
    
    def tt_amount(img_path):
        amount_img = img_path
        amount_text = pytesseract.image_to_string(amount_img, lang='tha+eng')
        uncleaned_sections = amount_text.split('\n')
        sections = []
        for section in uncleaned_sections:
                  sections.append(TextCorrections.clean_text(section.splitlines()))
        sec_list = list(filter(None, sections))
        text_totals_price = sec_list[-4][0].split() #total before vax
        text_amount = sec_list[-1][0].split() #Amount(totals+vax7%)
        tt = TextCorrections.collect_int_format(text_totals_price[1])
        total = TextCorrections.collect_float_format(tt)
        tt2 = TextCorrections.collect_int_format(text_amount[1])
        amount = TextCorrections.collect_float_format(tt2)
        print(tt)
        print(tt2)
        return [total, amount]
    
    def unit_peak(img_path):
        peak_units_img = img_path
        peak_units_text = pytesseract.image_to_string(Image.open(peak_units_img), lang='tha+eng')
        uncleaned_sections = peak_units_text.split('\n')
        sections = []
        for section in uncleaned_sections:
            sections.append(TextCorrections.clean_text(section.splitlines()))
        sec_list = list(filter(None, sections))
        on_peak_unit = TextCorrections.collect_int_format(sec_list[0][0])
        off_peak_unit = TextCorrections.collect_int_format(sec_list[1][0])
        on_peak = TextCorrections.collect_int_format(sec_list[2][0])
        off_peak = TextCorrections.collect_int_format(sec_list[3][0])
        power_factor = TextCorrections.collect_int_format(sec_list[-1][0])
        return [on_peak_unit, off_peak_unit, on_peak, off_peak, power_factor]
    
class OCR_electricity_bills_segment03:
    def __init__(self,bills_path):
        self.bills_path = bills_path  
    def segment_bills(self):
        img_path = self.bills_path
        im_np = np.frombuffer(img_path, np.uint8)
        img = cv2.imdecode(im_np, cv2.IMREAD_COLOR)
        down_width = 1080
        down_height = 1920
        down_points = (down_width, down_height)
        resized_down = cv2.resize(img, down_points, interpolation= cv2.INTER_LINEAR)
        a, b, c, d = 60, 400, 1000, 700
        a1, b1, c1, d1 = 100, 315, 410, 75
        im1 = cv2.rectangle(resized_down, (a,b), (a+c, b+d), (36,255,12),2)
        cropped = im1[b:b + d, a:a + c]
        im2 = cv2.rectangle(resized_down, (a1,b1), (a1+c1, b1+d1), (36,255,12),2)
        cropped2 = im2[b1:b1 + d1, a1:a1 + c1]
        cv2.imwrite("api/controller/ocr_electricity/e03crop_img/table.jpg",cropped)
        cv2.imwrite("api/controller/ocr_electricity/e03crop_img/cname_lo.jpg",cropped2)

class OCR_electricity_bills03:
    def ocr_tab(img_path):
        with open(img_path, 'rb') as f:
            crop_img = cv2.imdecode(np.frombuffer(f.read(), np.uint8), -1)
            gray_crop = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
            custom_config = r'--oem 3 --psm 4'
            com_lo_text = pytesseract.image_to_string(gray_crop, lang='tha+eng', config=custom_config)
            uncleaned_sections = com_lo_text.split('\n')
            sections = []
            for section in uncleaned_sections:
                sections.append(TextCorrections.clean_text(section.splitlines()))
            sec_list = list(filter(None, sections))

            def get_element(sec_list, index, split_char):
                try:
                        return sec_list[index][0].split(split_char)[-1]
                except:
                        return ''
            install_id = get_element(sec_list, 0, ' ')
            read_date = get_element(sec_list, 0, ' ')
            total_price = get_element(sec_list, -3, ' ')
            amount = get_element(sec_list, -1, ' ')
            units_P = get_element(sec_list, 1, ' ')
            units_OP = get_element(sec_list, 2, ' ')
            units_H = get_element(sec_list, 3, ' ')
            FT_units = get_element(sec_list, 5, ' ')
            kW_P = get_element(sec_list, 7, ' ')
            kW_OP = get_element(sec_list, 8, ' ')
            kW_H = get_element(sec_list, 10, ' ')
            
            bills_tab_information = {'installation_id':install_id,
                                'meter_read_date':read_date,
                                'FT_units':FT_units,
                                'price_before_tax':total_price,
                                'amount':amount}
            
            bills_tab_information['unit_peak'] = [{'name':'P_units',
                                                    'values':units_P,
                                                    'unit_name':'units'},
                                                    {'name':'OP_units',
                                                    'values':units_OP,
                                                    'unit_name':'units'},
                                                    {'name':'H_units',
                                                    'values':units_H,
                                                    'unit_name':'units'},
                                                    {'name':'P_kW',
                                                    'values':kW_P,
                                                    'unit_name':'kW'},
                                                    {'name':'OP_kW',
                                                    'values':kW_OP,
                                                    'unit_name':'kW'},
                                                    {'name':'H_kW',
                                                    'values':kW_H,
                                                    'unit_name':'kW'}]
            
            return bills_tab_information

    def ocr_cname_lo(img_path):
        crop_img = cv2.imread(img_path)
        gray_crop = cv2.cvtColor(crop_img,cv2.COLOR_BGR2GRAY)
        custom_config = r'--oem 3 --psm 4'
        com_lo_text = pytesseract.image_to_string(gray_crop, lang='tha+eng', config=custom_config)
        uncleaned_sections = com_lo_text.split('\n')
        sections = []
        for section in uncleaned_sections:
            sections.append(TextCorrections.clean_text(section.splitlines()))
        sec_list = list(filter(None, sections))
        try:
            list_name = sec_list[0][0].split()[1:]
        except:
            list_name = ''
        try:
            list_lo = sec_list[1][0].split()[1:]
        except:
            list_lo = ''
        com_name = ' '.join(list_name)
        location = ' '.join(list_lo)
        cname_lo_dic = {'company_name':com_name,
                        'locations':location}
        return cname_lo_dic




            
    

