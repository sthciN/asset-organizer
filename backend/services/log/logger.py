def log_into_sheet(google_sheet, sheet, worksheet_name, data):
    google_sheet.create_worksheet(sheet=sheet, worksheet_name=worksheet_name)
    google_sheet.append_row_into_worksheet(sheet=sheet, worksheet_name=worksheet_name, data=[data])
    raise Exception(worksheet_name)