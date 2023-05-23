import re
from pprint import pprint
from datetime import datetime
import os
import time
import sys


class TextCorrections:
    def clean_text(text) -> list:
        """Removes empty lines as well as leading and trailing spaces.
        Also removes EOL characters.
        Args:
            text (str/list): Input text
        Returns:
            (list): A list of strings"""
        if type(text) == str:
            splittext = text.splitlines()
            if len(splittext) == 1:
                print("Text is a single line string")
                return text
        elif type(text) == list:
            splittext = text
        result = []
        for line in splittext:
            cleaned = line.strip()
            if cleaned != "":
                result.append(cleaned)
        return result

    def collect_int_format(num_text):
        num = num_text.replace(",", "")
        num = num.replace('.', '')
        num = "{:,}".format(int(num))
        return num

    def collect_float_format(num_text):
        num1 = num_text.replace(",", "")
        deci_num = num1[-2:]
        num = num1[0:-2]
        num = num.replace(",", "")
        num = num.replace('.','')
        num = "{:,}".format(int(num))
        return str(num)+'.'+deci_num

    def collect_num(list_num):
        text_num = list_num
        tn = ''.join(text_num[0:-1])
        tn = "{:,}".format(int(tn))
        tn = str(tn)+'.'+list_num[-1]
        return tn
    
    def collect_num2int(num_text):
        num = num_text.replace(",", "")
        num = num.replace('.',"")
        num = num.replace('๐','0')
        if num.isdigit() == True:
            num = "{:,}".format(int(num))
        else:
            pass
        return num