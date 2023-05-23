from api.controller.ocr_plumping.ocr_plumping import OCR_plumping_bills
from flask import Flask, request, jsonify

class OCR_plumping_bills_API:
        def __init__(self,format_id,image_path):
                self.format_id = format_id
                self.image_path = image_path        
        def ocr_plumbing_bills(self):
                if self.format_id == 'p01':
                        ocr_plumbing_bills = OCR_plumping_bills(self.image_path)
                        ocr_plumbing_bills.segment_bills()
                        try:
                                cname_lo = ocr_plumbing_bills.ocr_comname_lo()
                        except:
                                cname_lo = ['','']
                
                        try:
                                tab = ocr_plumbing_bills.ocr_price_date_con()
                        except:
                                tab = ['','','','','','']
                
                        bills_informations = {'company_name':cname_lo[0],
                                        'location':cname_lo[-1],
                                        'account_no.':tab[0],
                                        'meter_read_before':tab[1],
                                        'meter_read_after':tab[2],
                                        'consumtions':tab[3],
                                        'price_before_tax':tab[4],
                                        'amount':tab[5]}
                
                        res_pay = {'company_name':bills_informations['company_name'],
                                        'locations':bills_informations['location'],
                                        'account_no.':bills_informations['account_no.'],
                                        'meter_read_before':bills_informations['meter_read_before'],
                                        'meter_read_after':bills_informations['meter_read_after'],
                                        'consumtions':bills_informations['consumtions'],
                                        'price_before_tax':bills_informations['price_before_tax'],
                                        'amount':bills_informations['amount']}
                        return res_pay
                else:
                        return "Format ID invalid"

