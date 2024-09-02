
import os
from services.google.drive import GoogleDrive
import multiprocessing
from datetime import datetime
from services.google.sheet import GoogleSheet, GoogleWorksheet
from .processor import png_processor


def png_provider():
    png_folder_id = os.environ.get('PNG_FOLDER_ID')
    new_folder_id = os.environ.get('NEW_FOLDER_ID')
    data_folder_id = os.environ.get('DATA_FOLDER_ID')
    sheet_name = os.environ.get('DATA_SHEET_NAME')
    log_folder_id = os.environ.get('LOG_FOLDER_ID')
    log_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    drive = GoogleDrive()
    google_sheet = GoogleSheet()
    data_sheet = google_sheet.open_sheets(folder_id=data_folder_id, sheet_name=sheet_name)
    google_worksheet = GoogleWorksheet(sheet=data_sheet)
    ui = google_worksheet.worksheet_data(worksheet_name='UI')
    files_data = google_worksheet.worksheet_data(worksheet_name='uac_assets_data')
    ads_data = google_worksheet.worksheet_data(worksheet_name='uac_ads_data')
    files_buyout_date = google_worksheet.worksheet_data(worksheet_name='buyouts_to_date')
    log_sheet = google_sheet.open_sheets(folder_id=log_folder_id, sheet_name=f'Logs-{log_time}')
    # backup_folder_id = drive.backup_folder(parent_id=data_folder_id, shared_folder_id=png_folder_id)
    # TODO put hte backup_folder_id
    file_list = drive.fetch_png_list(folder_id='1t2vEOwfBI6YwAfttJqHUkv_Vh6dhuwR-')

    for file in file_list[1:2]:
        try:
            png_processor(file, drive, new_folder_id, ui, files_data, ads_data, files_buyout_date, google_sheet, log_sheet)
            print('='*50)
            print('='*50)

        except Exception as error:
            print(error)
            print('='*50)
            print('='*50)
            continue

    # TODO Uncomment the code below
    num_cpus = os.cpu_count()
    # num_processes = num_cpus // 2
    # with multiprocessing.Pool(processes=num_processes) as pool:
    #     pool.starmap(png_processor, [(file, drive, new_folder_id, log_time) for file in file_list])
    