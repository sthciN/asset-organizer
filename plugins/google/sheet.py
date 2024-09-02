import gspread
from plugins.google.base import Google
from plugins.google.drive import GoogleDrive

class GoogleSheet(Google):
    def __init__(self):
        super().__init__()
        self.gc = gspread.authorize(self.creds)

    def create_sheet(self, folder_id, sheet_name):
        # Check if the sheet exists
        drive = GoogleDrive()
        sheet = drive.fetch_file_in_given_folder(folder_id=folder_id, file_name=sheet_name)
        if sheet:
            return None

        sheet = self.gc.create(title=sheet_name, folder_id=folder_id)

        return sheet
    
    def create_worksheet(self, sheet, worksheet_name):
        sheet = self.gc.open_by_key(sheet.id)
        
        # Check if worksheet exists
        try:
            worksheet = sheet.worksheet(worksheet_name)
        
        except:
            worksheet = sheet.add_worksheet(title=worksheet_name, rows="100", cols="10")
        
        return worksheet
    
    def append_row_into_worksheet(self, sheet, worksheet_name, data):
        sheet = self.gc.open_by_key(sheet.id)
        worksheet = sheet.worksheet(worksheet_name)
        existing_data = self.worksheet_data(sheet, worksheet_name)
        if data not in existing_data:
            worksheet.append_row(data)

    def open_sheets(self, folder_id, sheet_name):
        self.create_sheet(folder_id=folder_id, sheet_name=sheet_name)
        sheet = self.gc.open(title=sheet_name, folder_id=folder_id)
        return sheet

    def worksheet_data(self, sheet, worksheet_name):
        return sheet.worksheet(worksheet_name).get_all_values()[1:]
