import os
import time
import json
import logging
from services.api.open_ai import OpenAiImageAnalyzerSimulator
from fastapi import HTTPException


def image_quality_check_openai(image_bytes: bytes):
    api_key = os.environ['OPENAI_API_KEY']
    max_retries=3
    retry_delay=2
    
    openai_api = OpenAiImageAnalyzerSimulator(api_key=api_key)
    
    for _attempt in range(max_retries):
        try:
            result = openai_api.analyze_image(image_bytes=image_bytes)
            
            if 'error' in result:
                error = result['error']
                message = error['message']
                code = error['code']
                logging.error("Error: %s", message)
                raise HTTPException(detail=message, status_code=code)
            
            return result

        except HTTPException as http_excp:
            logging.error(http_excp.response.detail)

        except Exception as err:
            pass

        time.sleep(retry_delay)

    raise Exception("Failed to check quality after %s attempts", max_retries)