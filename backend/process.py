
import os
from services.google.drive import GoogleDrive
import multiprocessing
from datetime import datetime
from services.validation.validator import ValidFile
from services.api.budget import buyout_set_budget
from helper.utils import search_in_df
from services.google.sheet import GoogleSheet, GoogleWorksheet
from fastapi import HTTPException
from services.validation.media import open_image
from services.sql_app.crud import update_budget
from services.bids_budget.performance import calculate_performance_score, adjust_budget


def provider():
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
    

def png_processor(file, drive, new_folder_id, ui, files_data, ads_data, files_buyout_date, google_sheet, log_sheet):
    
    valid_file = ValidFile(file)
    
    # data = self.sheet.worksheet(worksheet_name).get_all_values() temporary
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

    file_id = search_in_df(dataframe=files_data,
                           search_column='asset_name',
                           search_value=valid_file.name.replace('_', '|'),
                           return_column='asset_id')

    if not valid_file.validate_buyout(files_data, files_buyout_date):
        try:
            worksheet_name = 'Asset Date Expired'
            ad_id = search_in_df(dataframe=ads_data, search_column='asset_id', search_value=file_id, return_column='ad_id')
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
    
    # try:
    #     # TODO Find the current budget from sheet
    #     budget = 1

    #     performance_score = calculate_performance_score()
    #     new_budget = adjust_budget(initial_budget=budget, performance_score=performance_score)
    #     update_budget(file_id=file_id, new_budget=new_budget)

    # except Exception as error:
    #     worksheet_name = 'Asset Performance Budget Update Failed'
    #     google_sheet.create_worksheet(sheet=log_sheet, worksheet_name=worksheet_name)
    #     google_sheet.append_row_into_worksheet(sheet=log_sheet, worksheet_name=worksheet_name, data=[valid_file.name])

    print('Move completed...')
