# num_cores = os.cpu_count()
# max_workers = max(num_cores // 2, 2)
# with ProcessPoolExecutor(max_workers=max_workers) as executor:
#     futures = []
#     for file in file_list[:4]:  # Process the first 4 files
#         futures.append(
#             executor.submit(
#                 png_processor, 
#                 file=file,
#                 drive=drive,
#                 new_folder_id=new_folder_id,
#                 ui=ui,
#                 files_data=files_data,
#                 ads_data=ads_data,
#                 files_buyout_date=files_buyout_date,
#                 google_sheet=google_sheet,
#                 log_sheet=log_sheet,
#             )
#         )

#     for future in as_completed(futures):
#             try:
#                 future.result()
#                 print('='*50)
#                 print('='*50)
#             except Exception as error:
#                 print(f"Error: {error}")
#                 print('='*50)
#                 print('='*50)
#                 continue


# threads = []
# log_results = []
# lock = threading.Lock()
# for file in file_list[:4]:
#     thread = threading.Thread(target=png_processor, args=(file,
#                                                           drive,
#                                                           new_folder_id,
#                                                           ui,
#                                                           files_data,
#                                                           ads_data,
#                                                           files_buyout_date,
#                                                           google_sheet,
#                                                           log_sheet))
#     threads.append(thread)
#     thread.start()

# for thread in threads:
#     thread.join()

# # Collecting log results
# print("All threads have finished.")
# print("Collected Results:")
# for result in log_results:
#     print(result)