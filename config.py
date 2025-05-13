import os
from dotenv import load_dotenv

def load_keys():
    load_dotenv()
    return {
        'apiKey': os.getenv('OKX_API_KEY'),
        'secret': os.getenv('OKX_API_SECRET'),
        'password': os.getenv('OKX_PASSPHRASE')
    }