import requests
import sys

try:
    r = requests.get('https://satguard-ai.onrender.com/health', timeout=90)
    print(f'Keep-alive ping: {r.status_code}')
except Exception as e:
    print(f'Keep-alive ping failed: {e}')

sys.exit(0)
