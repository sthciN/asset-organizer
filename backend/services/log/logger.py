def log_into_sheet(google_sheet, sheet, worksheet_name, data):
    try:
        worksheet = google_sheet.create_worksheet(sheet=sheet, worksheet_name=worksheet_name)
        worksheet.append_row([data])
    
    except Exception as error:
        # Logging failed
        print(f"Log failed error: {error}")
        raise Exception
