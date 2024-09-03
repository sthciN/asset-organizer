import os
from collections import defaultdict
from datetime import datetime
from fastapi import HTTPException
from services.google.drive import GoogleDrive
from services.google.sheet import GoogleSheet, GoogleWorksheet
from services.sql_app.database import SessionLocal
from .processor import png_processor
from tqdm import tqdm


task_statuses = defaultdict(str)


def png_provider(task_id: str):
    task_statuses[task_id] = 'In progress'
    png_folder_id = os.environ.get('PNG_FOLDER_ID')
    new_folder_id = os.environ.get('NEW_FOLDER_ID')
    data_folder_id = os.environ.get('DATA_FOLDER_ID')
    sheet_name = os.environ.get('DATA_SHEET_NAME')
    log_folder_id = os.environ.get('LOG_FOLDER_ID')
    log_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    drive = GoogleDrive()
    google_sheet = GoogleSheet()
    google_worksheet = GoogleWorksheet()

    try:
        backup_folder_id = drive.backup_folder(parent_id=data_folder_id, shared_folder_id=png_folder_id)
        file_list = drive.fetch_png_list(folder_id=backup_folder_id)
        print('len(file_list)', len(file_list))
        
        data_sheet = google_sheet.open_sheets(folder_id=data_folder_id, sheet_name=sheet_name)
        ui_ws = google_sheet.fetch_worksheet(sheet=data_sheet, worksheet_name='UI')
        files_data_ws = google_sheet.fetch_worksheet(sheet=data_sheet, worksheet_name='uac_assets_data')
        ads_data_ws = google_sheet.fetch_worksheet(sheet=data_sheet, worksheet_name='uac_ads_data')
        files_buyout_date_ws = google_sheet.fetch_worksheet(sheet=data_sheet, worksheet_name='buyouts_to_date')
        ui = google_worksheet.worksheet_data(worksheet=ui_ws)
        files_data = google_worksheet.worksheet_data(worksheet=files_data_ws)
        ads_data = google_worksheet.worksheet_data(worksheet=ads_data_ws)
        files_buyout_date = google_worksheet.worksheet_data(files_buyout_date_ws)
        files_buyout_date['buyout_code'] = files_buyout_date['buyout_code'].astype('string')
        log_sheet = google_sheet.create_sheet(folder_id=log_folder_id, sheet_name=f'Logs-{log_time}')
        
    
    except HTTPException as error:
        raise error
    
    for file in tqdm(file_list):
        db = SessionLocal()
        try:
            png_processor(file=file,
                          drive=drive,
                          new_folder_id=new_folder_id,
                          ui=ui,
                          files_data=files_data,
                          ads_data=ads_data,
                          files_buyout_date=files_buyout_date,
                          google_sheet=google_sheet,
                          log_sheet=log_sheet,
                          db=db)
            print('='*50)
            print('='*50)

        except Exception as error:
            print(error)
            print('='*50)
            print('='*50)
            continue

    task_statuses[task_id] = 'Completed'

    return None
