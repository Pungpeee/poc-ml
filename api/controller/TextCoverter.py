import datetime
class TextConverter:
    def __init__(self):
        self.text_to_number = {
                "i": "1",
                "I": "1",
                "j": "1",
                "J": "1",
                "!": "1",
                "¢": "4",
                "$": "5",
                "H": "8",
                "l": "1",
                "L": "1",
                "O": "0",
                "o": "0",
                "Z": "2",
                "s": "5",
                "S": "8",
                "B": "8",
                "b": "6",
                "g": "9",
                "q": "9",
                "t": "7",
                "y": "7",
                "z": "2",
                "e": "8"}
    def convert_text(self, text):
        for symbol, number in self.text_to_number.items():
            text = text.replace(symbol, number)
        return text
    def correct_date_format(self,date_text):
        date_components = date_text.split('/')
        current_year = str(datetime.datetime.now().year)
        day = date_components[0]
        month = date_components[1]
        year = date_components[-1]
        if day[0] == '9':
            day = '0'+day[-1]
        if month[0] == '9':
            month = '0'+month[-1]
        if int(year) > int(current_year):
            year = current_year
        date = day+'/'+month+'/'+year
        return date
