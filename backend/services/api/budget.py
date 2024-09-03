import os
import time
import logging
from services.api.google_ads import GoogleAdsApiSimulator
from fastapi import HTTPException


def buyout_set_budget_ok(asset_id, ad_id='ad_id', new_budget=1000.0):
    api_key = os.environ.get('GOOGLEADS_API_KEY')
    max_retries=3
    retry_delay=2
    google_ads_api = GoogleAdsApiSimulator(api_key=api_key)
    
    for _attempt in range(max_retries):
        try:
            print(1)
            result = google_ads_api.update_asset_budget(ad_id=ad_id, asset_id=asset_id, new_budget=new_budget)

            if 'error' in result:
                print(2)
                error = result['error']
                message = error['message']
                code = error['code']
                print(3)
                raise HTTPException(detail=message, status_code=code)

            print(7)
            return True
        
        except HTTPException as http_excp:
            print(3.5)
            print(http_excp.response.detail)
            pass

        except Exception:
            print(4)
            pass

        time.sleep(retry_delay)
        print(5)

    print(6)
    return False