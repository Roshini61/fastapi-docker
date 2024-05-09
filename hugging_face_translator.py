# from transformers import AutoTokenizer, TFBertTokenizer

# tokenizer = AutoTokenizer.from_pretrained("google-bert/bert-base-uncased")
# tf_tokenizer = TFBertTokenizer.from_tokenizer(tokenizer)

import json
import requests
import time

token_access = "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"
headers = {"Authorization": f"Bearer {token_access}"}

API_URL = "https://api-inference.huggingface.co/models/Helsinki-NLP/opus-mt-en-es"

def query(payload):
    
    data = json.dumps(payload)

    time.sleep(1)

    while True:

      try:
        
        response = requests.request("POST", API_URL, headers=headers, data=data)
        break
      
      except Exception:

          continue

    return json.loads(response.content.decode("utf-8"))
    
data = query(
    {
        "inputs": "venky is my mentor for life...",
    }
)

print(data)