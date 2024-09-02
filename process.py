
import os
from plugins.google.drive import GoogleDrive
import multiprocessing
from datetime import datetime
import logging
from plugins.validation.validator import ValidFile
from plugins.api.budget import buyout_set_budget
from helper.utils import get_file_id_from_worksheet, get_ad_id_from_worksheet
from plugins.google.sheet import GoogleSheet
from fastapi import HTTPException
from plugins.validation.media import open_image

def provider():
    logger = multiprocessing.get_logger()
    png_folder_id = os.environ.get('PNG_FOLDER_ID')
    new_folder_id = os.environ.get('NEW_FOLDER_ID')
    data_folder_id = os.environ.get('DATA_FOLDER_ID')
    
    drive = GoogleDrive()
    backup_folder_id = drive.backup_folder(parent_id=data_folder_id, shared_folder_id=png_folder_id)
    file_list = drive.fetch_png_list(folder_id=backup_folder_id)
    log_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    num_cpus = os.cpu_count()
    for file in file_list[1:2]:
        try:
            png_processor(file, drive, new_folder_id, log_time)
            print('='*50)
            print('='*50)

        except Exception as error:
            print(error)
            print('='*50)
            print('='*50)
            continue
        

    # TODO Uncomment the code below
    num_processes = num_cpus // 2
    # with multiprocessing.Pool(processes=num_processes) as pool:
    #     pool.starmap(png_processor, [(file, drive, new_folder_id, log_time) for file in file_list])
    

def png_processor(file, drive, new_folder_id, log_time):
    data_folder_id = os.environ.get('DATA_FOLDER_ID')
    sheet_name = os.environ.get('DATA_SHEET_NAME')
    log_folder_id = os.environ.get('LOG_FOLDER_ID')
    
    valid_file = ValidFile(file)
    google_sheet = GoogleSheet()
    data_sheet = google_sheet.open_sheets(folder_id=data_folder_id, sheet_name=sheet_name)
    ui = google_sheet.worksheet_data(sheet=data_sheet, worksheet_name='UI')
    files_data = google_sheet.worksheet_data(sheet=data_sheet, worksheet_name='uac_assets_data')
    log_sheet = google_sheet.open_sheets(folder_id=log_folder_id, sheet_name=f'Logs-{log_time}')
    
    # Populate the new file
    new_file = drive.populate_new_file(valid_file, files_data, ui)
    
    # Check if the file has a parent
    if None in new_file['parents']:
        worksheet_name = 'Invalid PNG Name'
        google_sheet.create_worksheet(sheet=log_sheet, worksheet_name=worksheet_name)
        google_sheet.append_row_into_worksheet(sheet=log_sheet, worksheet_name=worksheet_name, data=[valid_file.name])
        raise Exception(worksheet_name)

    print('file', file)

    # TODO Check the regex pattern and uncomment the code below
    # Validate the file name, buyout date, and OpenAI quality
    # if not valid_file.validate_png_name():
    #     worksheet_name = 'Invalid PNG Name'
    #     google_sheet.create_worksheet(sheet=log_sheet, worksheet_name=worksheet_name)
    #     google_sheet.append_row_into_worksheet(sheet=log_sheet, worksheet_name=worksheet_name, data=[valid_file.name])
    #     raise Exception(worksheet_name)
        # raise HTTPException(status_code=404, detail="Item not found")
    
    print('File name validation passed...')
    
    is_file_exist = drive.png_exists_in_folder(name=valid_file.name, parents=new_file.get('parents'), current_folder_id=new_folder_id)
    if is_file_exist:
        raise Exception('Asset already exists...')

    print('Checking for existence passed...')

    ads_data = google_sheet.worksheet_data(sheet=data_sheet, worksheet_name='uac_ads_data')
    files_buyout_date = google_sheet.worksheet_data(sheet=data_sheet, worksheet_name='buyouts_to_date')
    
    if not valid_file.validate_buyout(files_data, files_buyout_date):
        try:
            worksheet_name = 'Asset Date Expired'
            file_id = get_file_id_from_worksheet(name=valid_file.name, worksheet_values=files_data)
            ad_id = get_ad_id_from_worksheet(name=valid_file.name, worksheet_values=ads_data)
            buyout_set_budget(asset_id=file_id, ad_id=ad_id, new_budget=0.0)
            google_sheet.create_worksheet(sheet=log_sheet, worksheet_name=worksheet_name)
            google_sheet.append_row_into_worksheet(sheet=log_sheet, worksheet_name=worksheet_name, data=[valid_file.name])
            raise Exception(worksheet_name)
    
        except:
            worksheet_name = 'Asset Budget Update Failed'
            google_sheet.create_worksheet(sheet=log_sheet, worksheet_name=worksheet_name)
            google_sheet.append_row_into_worksheet(sheet=log_sheet, worksheet_name=worksheet_name, data=[valid_file.name])
            # raise Exception(worksheet_name)
    
    print('Buyout validation passed...')

    file_content = drive.png_content(file_id=valid_file.file_id)
    image = open_image(file_content)
    
    if not valid_file.quality_check(image_bytes=image):
        worksheet_name = 'Asset Quality Check Failed'
        google_sheet.create_worksheet(sheet=log_sheet, worksheet_name=worksheet_name)
        google_sheet.append_row_into_worksheet(sheet=log_sheet, worksheet_name=worksheet_name, data=[valid_file.name])
        raise Exception(worksheet_name)
    
    print('Quality check passed...')

    print(f'Moving file {valid_file.name}...')
    try:
        folder_id = drive.create_nested_folder(folder_names=new_file.get('parents'), parent_id=new_folder_id)
        
        drive.reorganize_png(file=new_file, folder_id=folder_id, image=image)
    
    except Exception as error:
        worksheet_name = 'Asset Move Failed'
        google_sheet.create_worksheet(sheet=log_sheet, worksheet_name=worksheet_name)
        google_sheet.append_row_into_worksheet(sheet=log_sheet, worksheet_name=worksheet_name, data=[valid_file.name])

    
    print('Move completed...')
