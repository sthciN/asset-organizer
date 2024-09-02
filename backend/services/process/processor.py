from services.process.validator import ValidFile
from services.api.budget import buyout_set_budget
from helper.utils import search_in_df
from services.process.media import open_image
from services.sql_app.crud import update_budget
from services.bids_budget.performance import calculate_performance_score, adjust_budget


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
    if not valid_file.validate_png_name():
        worksheet_name = 'Invalid PNG Name'
        google_sheet.create_worksheet(sheet=log_sheet, worksheet_name=worksheet_name)
        google_sheet.append_row_into_worksheet(sheet=log_sheet, worksheet_name=worksheet_name, data=[valid_file.name])
        raise Exception(worksheet_name)
    
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
