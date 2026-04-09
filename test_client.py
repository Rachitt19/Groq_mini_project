import requests

def test_api():
    # If testing Render URL, change this to your deployed URL
    url = "http://127.0.0.1:8000/ask"
    
    payload = {
        "prompt": "Write a basic python script for reading a CSV file"
    }
    
    print(f"Sending request to {url}...")
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        print("------------- RAW JSON -------------")
        # This will show literal \n characters
        print(data)
        print("\n\n------------- PROPERLY FORMATTED CODE -------------")
        # This will render it perfectly as human readable code
        print(data.get("answer", "No answer found"))
        
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        
if __name__ == "__main__":
    test_api()
