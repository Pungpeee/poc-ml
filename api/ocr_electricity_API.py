from api.controller.ocr_electricity.ocr_electricity import OCR_electricity_bills_segment01
from api.controller.ocr_electricity.ocr_electricity import OCR_electricity_bills01
from api.controller.ocr_electricity.ocr_electricity import OCR_electricity_bills_segment02
from api.controller.ocr_electricity.ocr_electricity import OCR_electricity_bills02
from api.controller.ocr_electricity.ocr_electricity import OCR_electricity_bills_segment03
from api.controller.ocr_electricity.ocr_electricity import OCR_electricity_bills03
from api.controller.text_functions import TextCorrections

class OCR_electricity_bills_API:
    def __init__(self,format_id,image_path):
        self.format_id = format_id
        self.image_path = image_path
    def ocr_electricity_bills(self):
        if self.format_id == 'e01':
            ocr_electricity_bills = OCR_electricity_bills_segment01(self.image_path)
            ocr_electricity_bills.segment_bills()
            img1 = 'api/controller/ocr_electricity/e01crop_img/01crop1.jpg'
            img0 = 'api/controller/ocr_electricity/e01crop_img/01crop0.jpg'
            img3 = 'api/controller/ocr_electricity/e01crop_img/01crop3.jpg'
            img2 = 'api/controller/ocr_electricity/e01crop_img/01crop2.jpg'
            img4 = 'api/controller/ocr_electricity/e01crop_img/01crop4.jpg'
            #information from bills
            header_value = OCR_electricity_bills01.find_header(img1)
            total_amount = OCR_electricity_bills01.find_amount(img0)
            list_unit_peak = OCR_electricity_bills01.find_unit_peak(img3,img2)
            install_id = OCR_electricity_bills01.find_installID(img4)
            #create a dictionary
            bills_information = {'company_name':header_value[2],
            'location':header_value[3],
            'installation_id':install_id,
            'meter_read_date':header_value[0],
            'power_unit/kWh':header_value[1],
            'price_before_tax':total_amount[0],
            'amount':total_amount[1]}
            if len(list_unit_peak) == 5:
                bills_information['unit_peak'] = [{'name':'on peak used',
                        'values':TextCorrections.collect_num2int(list_unit_peak[0]),
                                        'unit_name':'units'},
                                        {'name':'off peak used',
                                        'values':TextCorrections.collect_num2int(list_unit_peak[1]),
                                        'unit_name':'units'},
                                        {'name':'on peak',
                                        'values':TextCorrections.collect_num2int(list_unit_peak[2]),
                                        'unit_name':'kW'},
                                        {'name':'off peak',
                                        'values':TextCorrections.collect_num2int(list_unit_peak[3]),
                                        'unit_name':'kW'},
                                        {'name':'power factor',
                                        'values':TextCorrections.collect_num2int(list_unit_peak[4]),
                                        'unit_name':'kVAR'}
                                        ]
            elif len(list_unit_peak) == 4:
                    bills_information['unit_peak'] = [{'name':'on peak',
                                        'values':TextCorrections.collect_num2int(list_unit_peak[0]),
                                        'unit_name':'kW'},
                                        {'name':'partial peak',
                                        'values':TextCorrections.collect_num2int(list_unit_peak[1]),
                                        'unit_name':'kW'},
                                        {'name':'off peak',
                                        'values':TextCorrections.collect_num2int(list_unit_peak[2]),
                                        'unit_name':'kW'},
                                        {'name':'power factor',
                                        'values':TextCorrections.collect_num2int(list_unit_peak[3]),
                                        'unit_name':'kVAR'}
                                        ]
            else:
                pass
            res_pay = {'company_name':bills_information['company_name'],
                    'locations' : bills_information['location'],
                    'installation_id':bills_information['installation_id'],
                    'meter_read_date' : bills_information['meter_read_date'],
                    'power_unit/kWh': bills_information['power_unit/kWh'],
                    'price_before_tax': bills_information['price_before_tax'],
                    'amount': bills_information['amount'],
                    'unit_peak': bills_information['unit_peak']}
            return res_pay
        elif self.format_id == 'e02':
            ocr_electricity_bills = OCR_electricity_bills_segment02(self.image_path)
            ocr_electricity_bills.segment_bills()
            try:
                cname_lo = OCR_electricity_bills02.cname_location('api/controller/ocr_electricity/e02crop_img/comname.jpg')
            except:
                cname_lo = ['','']
            try:
                tab = OCR_electricity_bills02.ocr_tables('api/controller/ocr_electricity/e02crop_img/table.jpg')
            except:
                tab = ['','','','']
            try:
                tt_amo = OCR_electricity_bills02.tt_amount('api/controller/ocr_electricity/e02crop_img/table2.jpg')
            except:
                tt_amo = ['','']
            try:
                unit_p = OCR_electricity_bills02.unit_peak('api/controller/ocr_electricity/e02crop_img/peak.jpg')
            except:
                unit_p = ['','','','','']
            
            bills_information = {'company_name':cname_lo[0],
                            'location':cname_lo[1],
                            'installation_id':tab[0],
                            'meter_read_month':tab[1],
                            'meter_read_date':tab[2],
                            'power_unit/kWh':tab[3],
                            'price_before_tax':tt_amo[0],
                            'amount':tt_amo[1]}
            bills_information['unit_peak'] = [{'name':'on peak used',
                                        'values':unit_p[0],
                                        'unit_name':'units'},
                                        {'name':'off peak used',
                                        'values':unit_p[1],
                                        'unit_name':'units'},
                                        {'name':'on peak',
                                        'values':unit_p[2],
                                        'unit_name':'kW'},
                                        {'name':'off peak',
                                        'values':unit_p[3],
                                        'unit_name':'kW'},
                                        {'name':'power factor',
                                        'values':unit_p[4],
                                        'unit_name':'kVAR'}
                                        ]
            res_pay = {'company_name':bills_information['company_name'],
                    'locations' : bills_information['location'],
                    'meter_read_month':bills_information['meter_read_month'],
                    'meter_read_date' : bills_information['meter_read_date'],
                    'power_unit/kWh': bills_information['power_unit/kWh'],
                    'price_before_tax': bills_information['price_before_tax'],
                    'amount': bills_information['amount'],
                    'unit_peak': bills_information['unit_peak']}
            return res_pay
        elif self.format_id == 'e03':
            ocr_electricity_bills = OCR_electricity_bills_segment03(self.image_path)
            ocr_electricity_bills.segment_bills()
            cname_lo_dic = OCR_electricity_bills03.ocr_cname_lo("api/controller/ocr_electricity/e03crop_img/cname_lo.jpg")
            tab_dic = OCR_electricity_bills03.ocr_tab('api/controller/ocr_electricity/e03crop_img/table.jpg')
            bills_informations = {**cname_lo_dic, **tab_dic}
            
            res_pay = {'company_name': bills_informations['company_name'],
                        'locations': bills_informations['locations'],
                        'installation_id':bills_informations['installation_id'],
                        'meter_read_date':bills_informations['meter_read_date'],
                        'FT_units':bills_informations['FT_units'],
                        'price_before_tax':bills_informations['price_before_tax'],
                        'amount':bills_informations['amount'],
                        'units_peak': bills_informations['unit_peak']}
            return res_pay
        else:
            return 'Format ID invalid'