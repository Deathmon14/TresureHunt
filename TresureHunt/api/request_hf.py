import os
import requests

def ask_huggingface(prompt):
    API_URL = "https://api-inference.huggingface.co/models/EleutherAI/gpt-neo-2.7B"
    headers = {"Authorization": f"Bearer {os.getenv('HF_API_TOKEN')}"}
    
    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt}, timeout=10)
        if response.status_code == 200:
            # The API returns a list of generated completions
            data = response.json()
            # Adjust how you parse the response based on the API’s output format
            if isinstance(data, list) and len(data) > 0 and "generated_text" in data[0]:
                return data[0]["generated_text"]
            return "No response found"
        else:
            print(f"API Error: Status {response.status_code}")
            return "Error: API call failed."
    except Exception as e:
        print(f"Exception with Hugging Face API: {str(e)}")
        return "Error: Exception occurred."
