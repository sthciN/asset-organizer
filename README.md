# Overview
This project provides a solution for asset reorganization and processing.

The project structure is as follows:

```
├── README.md
├── backend # The backend service
│   ├── Dockerfile
│   ├── app
│   │   └── __init__.py
│   ├── credentials
│   │   └── service_account.json
│   ├── helper
│   │   └── utils.py
│   ├── main.py
│   ├── requirements.txt
│   ├── services
│   │   ├── api
│   │   │   ├── budget.py
│   │   │   ├── google_ads.py
│   │   │   ├── image_quality.py
│   │   │   └── open_ai.py
│   │   ├── bids_budget
│   │   │   └── performance.py
│   │   ├── google
│   │   │   ├── base.py # Authorizeation initialized.
│   │   │   ├── drive.py # GoogleDrive object, its properties and methods
│   │   │   └── sheet.py # GoogleSheet and GoogleWorksheet objects, their properties, and methods
│   │   ├── log
│   │   │   └── logger.py # Logging into a Google sheet
│   │   ├── process # The processing including the validations, quality check, and resizing
│   │   │   ├── media.py
│   │   │   ├── processor.py
│   │   │   ├── provider.py
│   │   │   ├── transformer.py
│   │   │   ├── utils.py
│   │   │   └── validator.py
│   │   └── sql_app # PostgreSQL
│   │       ├── crud.py
│   │       ├── database.py # Initialization
│   │       ├── models.py
│   │       └── schemas.py
├── docker-compose.yml
└── frontend # The frontend service
    ├── Dockerfile
    ├── package.json
    ├── public
    │   └── index.html
    └── src
        ├── App.css
        ├── App.js
        └── index.js
```


# Features
## Feature 1: Asset Reorganization
1. Read Settings
   
    Note: To avoid nested folder conflicts when levels change, update the NEW_FOLDER_ID in the environment variables.

3. Reorganize Assets

    1. Backup and Reorganization
        
        Each time the script runs, it keeps a backup of the homework_items Drive folder and reorganizes them in the folder with the id set as NEW_FOLDER_ID in the `.env`.

    2. The script duplicates files to the new folder called `Backup Folder`, it creates this folder if it doesn't exist. This folder will lay down in the DATA_FOLDER_ID folder where the data sheet exists.
    3. Files with the same name are not duplicated; they are moved if needed.
    4. Assets fetched are .png files and resized to <100kb.

## Feature 2: Asset Processing
### Validate Assets

- Naming Validation: Assets are validated against a regex pattern.
- Buyout Expiration Check: Expired assets are detected using their buyout code. Their budget is set to zero using the mocked API, with retry logic (3 attempts with delay).
- Quality Check: Images are analyzed using the mocked OpenAI API. Only images with quality > 5 and privacy_compliant: True proceed.


## Feature 3: Ads Budget Management

### Update Budgets Based on Asset Performance**
- Every time the script runs, it uses the mocked API provided to update budgets based on asset performance.
- Performance Calculation:

     ```python
     performance = (conversions / cost_per_conversion) + \
                   (all_conversions / cost_per_all_conversions) + \
                   (clicks / cost_micros * 1_000_000) + \
                   (impressions / cost_micros * 1_000_000)
     ```
- Budget Adjustment:
    - Top-performing assets are those with performance scores more than the avg performance of all the assets + 10% as the threshold. 
    - Increase: Increase the budget by 20% in database and api.
    - Decrease: Decrease the budget by 20% in database and api.

### Provide Feedback

- Logging: Logs the names of the assets into a specified sheet named as `Logs-{starting-process-datetime}`, different worksheets made for validation failure in the LOG_FOLDER_ID.
    - The name of the worksheets are: 
        `Unmatched PNG Name`
        `Asset Date Expired`
        `Asset Budget Update Failed`
        `Asset Budget Update Failed`
        `Asset Quality Check Failed`
        `Asset Move Failed`
        `Asset Performance Budget Update Failed`
- Error Handling: New logs are created for each run, allowing for tracking of file processing status.

## Deployment

1. Setup Environment Variables

Create a `.env` file within the backend folder with the following variables:
```
PNG_FOLDER_ID: The ID of the folder where the original assets are located.
DATA_FOLDER_ID: The ID of the folder where the Backup Folder and the data sheet are located.
DATA_SHEET_NAME: The name of the Data sheet
NEW_FOLDER_ID: The ID of the new folder where files will be reorganized.
LOG_FOLDER_ID: The ID of the folder where logs will be written.
GOOGLEADS_API_KEY: The API key used for Googleads API.
OPENAI_API_KEY: The API key used for OpenAI API.
POSTGRES_USER: The PostgreSQL username.
POSTGRES_PASSWORD: The PostgreSQL password
POSTGRES_DB: The name of the PostgreSQL database.
```
2. Add the POSTGRES_USER, POSTGRES_PASSWORD, and POSTGRES_DB values to the `docker-compose.yml` configuration.
3. Copy your [`service_account.json`](#google-api-setup) into the credentials folder.
4. Run `docker-compose up --build` to build and start the Docker containers.
5. Access Frontend at `http://localhost:3000/`.

### Frontend
The `Fetch File List` button is only for seeing the files in the PNG_FOLDER_ID. After clicking on the `Start`, a task starts in the background in the backend service. It processes all the assets in the PNG_FOLDER_ID. The frontend has a polling mechanism that requests the status of the task. If it becomes completed the `Start` buttons will be enabled again for a fresh processing. Otherwise, the user will see the processing is still in progress. It's safe to process the files again and again. You can adjust the chunks of the files to be processed in the `provider.py` file.

### Technical Details
- Backend: FastAPI that handles the processing task in background.
- Frontend: React
- Database: PostgreSQL (chosen for multithreading capabilities)
- Programming Language: Python 3.12
- Libraries:
    - `Pillow` for resizing the image
    - `google-api-python-client` for Google Drive
    - `gspread` for Google Sheets
    - `pandas` for data manipulation
    - `SQLAlchemy` for ORM

### Google API Setup

1. Enable APIs

- [Google Drive API](https://console.cloud.google.com/apis/enableflow?apiid=drive.googleapis.com)
- [Google Sheets API](https://console.cloud.google.com/apis/enableflow?apiid=sheets.googleapis.com)

2. Generate Key
    Create a service account and add the client email to the data sheet. 

3. Add Creds
    Move the generated key to the credentials folder and rename it to `service_account.json`.
4. Give the client email access to the folders and files that have been set in the `.env`.


## Known Issues and Considerations
- All the files in the `homework_item` will be processed and processing each file takes a long time.
- Parallelism: Google Drive APIs do not handle parallelism well, leading to SSL and authorization errors in multithreading.
- Validation Process: Validations are performed sequentially (see [Assumptions](#assumptions)). Future improvements could include parallel __file__ processes.
- Testing: Automated tests are necessary. The app should include unit, integration, and end-to-end tests to cover all functionalities.

## Assumptions
- File Naming and Asset Management: Instead of asset or asset_id, I used file and file_id across the app for clear and consistent naming.
- Validations are assumed to be in order. The reason for this is because if the name is not validated, the next step will not be meaningful to be executed. Same with the buyout date which doesn't need to be checked for quality. However, the unique name of the assets will be stored in the log files for future checking and see at what stage it is invalid.
- The asset names do not relate to ad_id in uac_ads_data. Static but random ad_id is used for budget updates.
- The `Backup Folder` will be created in the data folder next to the data file.

## Future Improvements
- Logging Enhancements: Considering a separate threaded logging for improved performance.
- Parallel Processing: Implementing parallelism by using databases for logging and creating a task queue for each file
