import time
import requests 

def check_website(url: str, timeout: int = 5) -> dict: 
    start_time = time.perf_counter()

    try: 
        response = requests.get(url, timeout=timeout)
        response_time = time.perf_counter() - start_time

        return {
            "url": url, 
            "status_code": response.status_code,
            "response_time_ms": response_time, 
            "is_up": response.status_code == 200,
            "error": None, 
        }
    except requests.RequestException as exc: 
        return {
            "url": url,
            "status_code": None,
            "response_time_ms": None,
            "is_up": False,
            "error": str(exc),
        }