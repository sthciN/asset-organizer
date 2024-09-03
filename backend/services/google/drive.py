import logging
from fastapi import HTTPException
from .base import Google
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from services.process.transformer import resize_png
from googleapiclient.http import MediaIoBaseUpload

class GoogleDrive(Google):
    
    def __init__(self):
        super().__init__()
        self.service = build("drive", "v3", credentials=self.creds)

    def fetch_file_in_given_folder(self, folder_id, file_name):
        query = f"'{folder_id}' in parents and name='{file_name}'"
        response = self.service.files().list(q=query).execute()
        files = response.get('files', [])
        if not files:
            return None
        else:
            return files[0]

    def fetch_png_list(self, folder_id):
        try:
            file_list = []
            page_token = None
            query = f"'{folder_id}' in parents" #  and mimeType='image/png'
            
            while True:
                response = self.service.files().list(
                        q=query,
                        spaces="drive",
                        fields="nextPageToken, files(id, name, size)",
                        pageToken=page_token,
                    ).execute()

                file_list.extend(response.get("files", []))
                page_token = response.get("nextPageToken", None)
                
                if page_token is None:
                    break

        except Exception as error:
            print(f"An error occurred: {error}")
            raise HTTPException(status_code=502, detail="Failed to fetch data from Google Drive. Please try again later.")

        return file_list

    def populate_new_file(self, valid_file, files_data, ui):
        parents = valid_file.decode_file_parents(files_data=files_data, ui=ui)
        new_file = {
            'name': valid_file.name,
            'size': int(valid_file.size),
            'fileId': valid_file.file_id,
            'parents': parents
            }
        
        return new_file

    def png_content(self, file_id):
        request = self.service.files().get_media(fileId=file_id)
        response = request.execute()
        return response

    def reorganize_png(self, file, folder_id, image):
        try:
            max_size = 100 * 1024
            new_file = {'name': file.get('name'), 'parents': [folder_id]}
            
            if file.get('size', 0) <= max_size:
                self.service.files().copy(fileId=file.get('fileId'), body=new_file).execute()

            else:
                resized_image = resize_png(image=image, max_size=max_size)
                media = MediaIoBaseUpload(resized_image, mimetype='image/png', resumable=True)
                
                # Upload the resized image
                file = self.service.files().create(
                    body=new_file,
                    media_body=media,
                    fields='id'
                ).execute()
        
        except Exception as error:
            print(f"An error occurred: {error}")

    def create_nested_folder(self, folder_names, parent_id):
        for folder_name in folder_names:
            # Search for the folder in the parent folder
            query = f"'{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and name='{folder_name}'"
            response = self.service.files().list(q=query).execute()

            # If the folder exists, use its ID as the parent ID for the next iteration
            # If it doesn't exist, create it and use its ID as the parent ID for the next iteration
            if response.get('files'):
                parent_id = response.get('files')[0].get('id')
            
            else:
                file_metadata = {
                    'name': folder_name,
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [parent_id]
                }
                folder = self.service.files().create(body=file_metadata, fields='id').execute()
                parent_id = folder.get('id')

        return parent_id

    def png_exists_in_folder(self, name, parents, current_folder_id):
        parent_ids = []
        pid = current_folder_id
        for parent_name in parents:
            id = self.fetch_folder_id_by_name(parent_name, pid)
            if id:
                pid = id
                parent_ids.append(id)

            else:
                return False

        query = f"'{pid}' in parents and name='{name}'"
        response = self.service.files().list(q=query).execute()
        if response.get('files'):
            return True

        return False

    def search_png_in_folders(self, name, parents):
        query = f"name='{parents[0]}' and mimeType='application/vnd.google-apps.folder'"
        results = self.service.files().list(q=query, fields='files(id, name)').execute().get('files', [])

        for result in results:
            if result['name'] == parents[0]:
                if len(parents) == 1:
                    # If we're at the last folder, search for the file
                    file_query = f"name='{name}' and parentId='{result['id']}' and mimeType='image/png'"
                    response = self.service.files().list(q=file_query).execute().get('files', [])
                    print('response', response)
                    if response:
                        return response[0]['id']
                else:
                    # Recursively search the next folder
                    return self.search_png_in_folders(result['id'], parents[1:], name)

        return None

    def png_exists_in_folder_id(self, name, parent_id):
        query = f"{parent_id} in parents and name='{name}'"
        response = self.service.files().list(q=query).execute()
        if response.get('files'):
            print('file exists FINALLY')
            return True

        return False
    
    def fetch_folder_id_by_name(self, name, parent_id):
        query = f"'{parent_id}' in parents and name='{name}'"
        response = self.service.files().list(q=query).execute()
        if response.get('files'):
            return response.get('files')[0].get('id')
        return None

    def backup_folder(self, parent_id, shared_folder_id):
        name = 'Backup Folder'
        
        # Check if the backup folder exists
        backup_folder_id = self.fetch_folder_id_by_name(name, parent_id)
        if not backup_folder_id:
            # Create a new folder in Drive for the backup
            file_metadata = {
                'name': name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_id]
            }
            backup_folder = self.service.files().create(body=file_metadata, fields='id').execute()
            backup_folder_id = backup_folder.get('id')
        
        # Get the list of files in the shared folder
        file_list = []
        page_token = None
        while True:
            print('page_token', page_token)
            query = f"'{shared_folder_id}' in parents"
            response = self.service.files().list(
                q=query,
                fields="nextPageToken, files(id, name)",
                pageToken=page_token,
                ).execute()
            
            file_list.extend(response.get("files", []))
            page_token = response.get("nextPageToken", None)
            
            if page_token is None:
                break

        # Copy each file to the backup folder
        print('Copying file...')
        for file in file_list:
            backup_file = self.fetch_file_in_given_folder(file_name=file.get('name'), folder_id=backup_folder_id)
            if backup_file:
                continue

            file_metadata = {
                'name': file.get('name'),
                'parents': [backup_folder_id]
            }
            self.service.files().copy(fileId=file.get('id'), body=file_metadata).execute()

        print('Backup completed.')
        return backup_folder_id
