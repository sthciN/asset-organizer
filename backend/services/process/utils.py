import pandas as pd
import random
from helper.utils import search_in_df_return_multiple_columns

def get_file_metrics_from_worksheet(file_id, ads_data):
    # TODO Randomly rutrn ad_id from data
    sample = [
        {'asset_id': 88342027808, 'ad_id': 592562914783},
        {'asset_id': 84857342861, 'ad_id': 592562914786},
        {'asset_id': 93021333234, 'ad_id': 592562915488},
        ]
    random_ad_id = random.choice(sample)['ad_id']

    # The ad_id is not unique, however the function returns the first value found
    columns = ['ad_id', 'all_conversions', 'conversions', 'clicks', 'impressions', 'cost_per_all_conversions', 'cost_per_conversion']
    data = search_in_df_return_multiple_columns(dataframe=ads_data,
                        search_column='ad_id',
                        search_value=random_ad_id,
                        return_columns=columns)
    
    data = data.astype('float')
    return data
