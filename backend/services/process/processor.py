from multiprocessing import Queue
from services.process.validator import ValidFile
from services.api.budget import buyout_set_budget_ok
from helper.utils import search_in_df
from services.process.media import open_image
from services.sql_app.crud import update_budget, get_budget, create_budget
from services.google.drive import GoogleDrive
from services.google.sheet import GoogleSheet
from services.log.logger import log_into_sheet
from services.bids_budget.performance import calculate_performance_score, adjust_budget
from services.process.utils import get_file_metrics_from_worksheet

def png_processor(file: dict,
                  drive: GoogleDrive,
                  new_folder_id: str,
                  ui: dict,
                  files_data: dict,
                  ads_data: dict,
                  files_buyout_date: dict,
                  google_sheet: GoogleSheet,
                  log_sheet: str,
                  db) -> None:
    
    valid_file = ValidFile(file)
    
    # Populate the new file
    new_file = drive.populate_new_file(valid_file, files_data, ui)
    print('new_file', new_file)

    # Check if the file is not orphaned
    if None in new_file['parents']:
        worksheet_name = 'Unmatched PNG Name'
        log_into_sheet(google_sheet, log_sheet, worksheet_name, valid_file.name)
        raise Exception(worksheet_name)

    if not valid_file.validate_png_name():
        worksheet_name = 'Unmatched PNG Name'
        log_into_sheet(google_sheet, log_sheet, worksheet_name, valid_file.name)
        raise Exception(worksheet_name)
    
    print('File name validation passed...')
    
    is_file_exist = drive.png_exists_in_folder(name=valid_file.name, parents=new_file.get('parents'), current_folder_id=new_folder_id)
    if is_file_exist:
        raise Exception('Asset already exists...')

    print('Checking for existence passed...')
    
    file_id = search_in_df(dataframe=files_data,
                            search_column='asset_name',
                            search_value=valid_file.name,
                            return_column='asset_id')

    try:
        worksheet_name = 'Asset Date Expired'
        
        not_expired = valid_file.validate_buyout(files_data, files_buyout_date)
        if not not_expired:
            log_into_sheet(google_sheet, log_sheet, worksheet_name, valid_file.name)
            
            # Update budget to 0.0
            try:
                # TODO ad_id should come from the sheet using search_in_df(), however the current data sheet is not updated
                ad_id = 3423856768
                budget_updated = buyout_set_budget_ok(asset_id=file_id, ad_id=ad_id, new_budget=0.0)
                if not budget_updated:
                    worksheet_name = 'Asset Budget Update Failed'
                    log_into_sheet(google_sheet, log_sheet, worksheet_name, valid_file.name)
            
            except:
                worksheet_name = 'Asset Budget Update Failed'
                log_into_sheet(google_sheet, log_sheet, worksheet_name, valid_file.name)

            raise Exception(worksheet_name)
    
    except:
        log_into_sheet(google_sheet, log_sheet, worksheet_name, valid_file.name)
        raise Exception(worksheet_name) 
    
    print('Buyout validation passed...')

    try:
        file_content = drive.png_content(file_id=valid_file.file_id)
        image = open_image(file_content)
        
        if not valid_file.quality_check(image_bytes=image):
            raise Exception
    
    except Exception:
        worksheet_name = 'Asset Quality Check Failed'
        log_into_sheet(google_sheet, log_sheet, worksheet_name, valid_file.name)
        raise Exception(worksheet_name)

    print('Quality check passed...')
    print(f'Moving file {valid_file.name}...')

    try:
        folder_id = drive.create_nested_folder(folder_names=new_file.get('parents'), parent_id=new_folder_id)
        drive.reorganize_png(file=new_file, folder_id=folder_id, image=image)
    
    except Exception as error:
        worksheet_name = 'Asset Move Failed'
        log_into_sheet(google_sheet, log_sheet, worksheet_name, valid_file.name)
        raise Exception(worksheet_name)
    
    # Performance
    try:
        metrics = get_file_metrics_from_worksheet(file_id=file_id, ads_data=ads_data)
        budget = get_budget(db=db, file_id=str(file_id))
        
        performance_score = calculate_performance_score(*metrics)
        if not budget:
            new_budget = adjust_budget(initial_budget=1000, performance_score=performance_score)
            create_budget(db=db, name=valid_file.name, file_id=str(file_id), budget=new_budget)
        
        else:
            new_budget = adjust_budget(initial_budget=budget.budget, performance_score=performance_score)
            update_budget(db=db, file_id=str(file_id), new_budget=new_budget)

    except:
        worksheet_name = 'Asset Performance Budget Update Failed'
        log_into_sheet(google_sheet, log_sheet, worksheet_name, valid_file.name)

    print('Move completed...')
