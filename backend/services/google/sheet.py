import gspread
import pandas as pd
from services.google.base import Google
from services.google.drive import GoogleDrive

class GoogleSheet(Google):
    
    def __init__(self):
        super().__init__()
        self.gc = gspread.authorize(self.creds)

    def create_sheet(self, folder_id, sheet_name):
        # Check if the sheet exists
        drive = GoogleDrive()
        sheet = drive.fetch_file_in_given_folder(folder_id=folder_id, file_name=sheet_name)
        if not sheet:
            sheet = self.gc.create(title=sheet_name, folder_id=folder_id)

        return sheet

    def open_sheets(self, folder_id, sheet_name):
        self.create_sheet(folder_id=folder_id, sheet_name=sheet_name)
        sheet = self.gc.open(title=sheet_name, folder_id=folder_id)
        
        return sheet
    
    def create_worksheet(self, sheet, worksheet_name):
        sheet = self.gc.open_by_key(sheet.id)
        
        # Check if worksheet exists
        try:
            worksheet = sheet.worksheet(worksheet_name)
        
        except:
            worksheet = sheet.add_worksheet(title=worksheet_name, rows="1000", cols="10")
        
        return worksheet
    
    def fetch_worksheet(self, sheet, worksheet_name):
        sheet = self.gc.open_by_key(sheet.id)
        worksheet = sheet.worksheet(worksheet_name)
        
        if not worksheet:
            return None
        
        return worksheet

class GoogleWorksheet(GoogleSheet):

    def __init__(self):
        super().__init__()

    def append_row_into_worksheet(self, worksheet, data):
        existing_data = self.worksheet_data(worksheet)
        
        # The data is a list, however the app expects one row at a time
        if existing_data[existing_data.columns[0]].str.contains(data[0]).any():
            return None
        
        worksheet.append_row(data)

    def worksheet_data(self, worksheet):
        data = worksheet.get_all_records()
        df = pd.DataFrame(data[1:], columns=data[0])

        return df
