import pandas as pd

def get_file_metrics_from_worksheet(file_id, worksheet_values):
    data = [
        {'asset_id': 88342027808, 'ad_id': 592562914783},
        {'asset_id': 84857342861, 'ad_id': 592562914786},
        {'asset_id': 93021333234, 'ad_id': 592562915488},
        ]

    ad_id = [d['ad_id'] for d in data if d['asset_id'] == file_id][0]
    # TODO update the return value

    return [86, 978]