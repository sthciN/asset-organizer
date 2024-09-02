def log_into_sheet(google_sheet, sheet, worksheet_name, data):
    worksheet = google_sheet.create_worksheet(sheet=sheet, worksheet_name=worksheet_name)
    google_sheet.append_row_into_worksheet(worksheet=worksheet, data=[data])
