import os
import re
import json
from datetime import datetime
from services.api.open_ai import OpenAiImageAnalyzerSimulator
from helper.utils import search_in_df
from .utils import get_file_metrics_from_worksheet


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
        
        # Check if the file buyout date is less than the file date or the current date
        if self.file_buyout_date < self.file_date or self.file_buyout_date < datetime.now():
            return False
        
        return True
    
    def get_buyout_date(self, files_buyout_date):
        buyout = self.name_meta_list[1]
        expiration_date = search_in_df(dataframe=files_buyout_date,
                                       search_column='buyout_code',
                                       search_value=buyout,
                                       return_column='expire_date')
        
        file_buyout_date = datetime.strptime(expiration_date, '%m/%d/%Y')
        
        if not file_buyout_date:
            return None
        
        return file_buyout_date
    
    def get_file_date(self, files_data):
        file_date = search_in_df(dataframe=files_data,
                                 search_column='asset_name',
                                 search_value=self.name.replace('_', '|'),
                                 return_column='asset_production_date')

        if not file_date:
            return None
        
        return datetime.strptime(file_date, '%Y-%m-%d %H:%M:%S')

    def decode_file_parents(self, files_data, ui):
        file_date = self.get_file_date(files_data)
        year = file_date.year if file_date else None
        month = file_date.month if file_date else None
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
        
        ui_sorted = ui.sort_values(by='level')
        result = [parent_dict.get(field) for field in ui_sorted['field']]

        return result

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

    def get_file_performance_metrics(self, ads_data):
        ad_id = get_file_metrics_from_worksheet(name=self.name.replace('_', '|'), worksheet_values=ads_data)
        api_key = os.environ.get('GOOGLEADS_API_KEY')
        return calculate_performance_score(ad_id=ad_id, api_key=api_key)