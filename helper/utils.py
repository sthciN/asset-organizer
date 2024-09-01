
def get_levels(ui_levels):
    ui_dict = {}
    for level in ui_levels:
        try:
            ui_dict[int(level[0].split('_')[1])] = level[1]
        
        except Exception as error:
            print(f"An error occurred: {error}")
            continue
    
    result = [ui_dict[i] for i in sorted(ui_dict.keys())]
    
    return result
    


def get_file_date_from_worksheet(name, worksheet_values):
    date = None
    for row in worksheet_values:
        if name in row[7]:
            date = row[11]
            break
    
    return date

def get_file_id_from_worksheet(name, worksheet_values):
    file_id = None
    for row in worksheet_values:
        if name in row[7]:
            file_id = row[0]
            break
    
    return file_id

def get_file_expiration_from_worksheet(buyout, worksheet_values):
    expiration = None
    for row in worksheet_values:
        if buyout in row[0]:
            expiration = row[1]
            break
    
    return expiration

def get_ad_id_from_worksheet(name, worksheet_values):
    return '592562915491'
    ad_id = None
    for row in worksheet_values:
        if name in row[7]:
            ad_id = row[3]
            break

    return ad_id


