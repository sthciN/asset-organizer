import os
import re
import json
from datetime import datetime
from plugins.api.open_ai import OpenAiImageAnalyzerSimulator
from helper.utils import get_file_date_from_worksheet, get_file_expiration_from_worksheet, get_levels

class ValidFile:

    def __init__(self, file):
        self.file = file
        self.name = file.get('name')
        self.size = file.get('size')
        self.file_id = file.get('id')
        self.name_meta_list = self.name.split(' _ ')
        self.file_buyout_date = None
        self.file_date = None

    def validate_png_name(self):
        pattern = r'^[A-Z]{2,3}-[A-Z]{2} _ (D0000|P0020|0000|P0000|P0022|P0010|D0238|00000|P0009|P00010|D0858) _ [\w &-]+ _ \d+x\d+ _ \d+s _ ?'
        if not re.match(pattern, self.name):
            return False
        
        # TODO write the file name somewhere for reporting
        return True
    
    def validate_buyout(self, files_data, files_buyout_date):
        self.file_buyout_date = self.get_buyout_date(files_buyout_date)
        if not self.file_buyout_date:
            return False
        
        self.file_date = self.get_file_date(files_data)
        if not self.file_date:
            return False
        
        if self.file_buyout_date < self.file_date:
            return False
        
        return True
    
    def get_buyout_date(self, files_buyout_date):
        buyout = self.name_meta_list[1]
        
        file_buyout_date = datetime.strptime(
            get_file_expiration_from_worksheet(
                buyout=buyout,
                worksheet_values=files_buyout_date
                ), '%m/%d/%Y')
        
        if not file_buyout_date:
            return None
        
        return file_buyout_date
    
    def get_file_date(self, files_data):
        file_date = get_file_date_from_worksheet(name=self.name.replace('_', '|'), 
                                                             worksheet_values=files_data)
        
        if not file_date:
            return None
        
        return datetime.strptime(file_date, '%Y-%m-%d %H:%M:%S')
    
    def decode_file_parents(self, files_data, ui):
        year = self.get_file_date(files_data).year
        month = self.get_file_date(files_data).month
        country = self.name_meta_list[0].split('-')[0].strip()
        language = self.name_meta_list[0].split('-')[1].strip()
        audience = self.name_meta_list[3].strip()
        transaction_side = self.name_meta_list[4].strip()
        
        parent_dict = {
            'country': country,
            'language': language,
            'audience': audience,
            'year': year,
            'month': month,
            'transaction_side': transaction_side
            }

        return [parent_dict[l] for l in get_levels(ui_levels=ui)]

    def quality_check(self, image_bytes: bytes) -> bool:
        # TODO Error handling
        api_key = os.environ['OPENAI_API_KEY']
        response = OpenAiImageAnalyzerSimulator(api_key=api_key).analyze_image(image_bytes=image_bytes)
        analyzed_data = json.loads(response)
        quality = analyzed_data.get('quality')
        privacy_compliance = analyzed_data.get('privacy')
        
        if quality < 5 or not privacy_compliance:
            # TODO Error handling
            # raise ValueError(f"Quality: {quality}, Privacy Compliance: {privacy_compliance}")
            return False
        
        return True
