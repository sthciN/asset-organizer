import os
from plugins.api.google_ads import GoogleAdsApiSimulator

def buyout_set_budget(asset_id, ad_id='ad_id', new_budget=1000.0):
    # TODO Error handling
    api_key = os.environ.get('GOOGLEADS_API_KEY')
    GoogleAdsApiSimulator(api_key=api_key).update_asset_budget(ad_id=ad_id, asset_id=asset_id, new_budget=new_budget)
