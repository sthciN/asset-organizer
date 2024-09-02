def get_ad_id_from_worksheet(name, worksheet_values):
    return '592562915491'

def search_in_df(dataframe, search_column, search_value, return_column):
    return dataframe[dataframe[search_column] == search_value][return_column].values[0]

def search_in_df_return_multiple_columns(dataframe, search_column, search_value, return_columns):
    return dataframe[dataframe[search_column] == search_value][return_columns].values[0]
