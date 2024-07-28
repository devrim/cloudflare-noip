import json
import os
import logging
import urllib.request
import urllib.error
import urllib.parse

# Set up logging
logging.basicConfig(filename='/tmp/cloudflare-noip.txt', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Read Cloudflare credentials
credentials_path = os.path.expanduser('~/.cloudflare-noip/keys.json')
if not os.path.exists(credentials_path):
    logging.error("The file ~/.cloudflare-noip/keys.json does not exist.")
    logging.info("Please create the folder ~/.cloudflare-noip/keys.json with the following structure:")
    logging.info('''{
    "api_key": "your_cloudflare_api_key",
    "email": "your_cloudflare_email",
    "zone_id": "your_cloudflare_zone_id"
}''')
    exit(1)
    
with open(credentials_path, 'r') as f:
    credentials = json.load(f)

API_KEY = credentials['api_key']
EMAIL = credentials['email']
ZONE_ID = credentials['zone_id']

# API endpoint
base_url = f'https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records'

# Headers for authentication
headers = {
    'X-Auth-Email': EMAIL,
    'X-Auth-Key': API_KEY,
    'Content-Type': 'application/json'
}

def update_record(record_name, record_type, content, proxied=True):
    # Find the existing record
    params = urllib.parse.urlencode({'name': record_name, 'type': record_type})
    url = f'{base_url}?{params}'
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            if not data['success']:
                logging.error(f"Response: {data}")
                logging.error(f"Error: {data['errors'][0]['message']}")
                exit(1)
            
            records = data['result']
    except urllib.error.URLError as e:
        logging.error(f"Failed to get records: {e}")
        exit(1)
    
    if records:
        record_id = records[0]['id']
        update_url = f'{base_url}/{record_id}'
        data = {
            'type': record_type,
            'name': record_name,
            'content': content,
            'ttl': 1,  # Auto TTL
            'proxied': proxied
        }
        req = urllib.request.Request(update_url, data=json.dumps(data).encode(), headers=headers, method='PUT')
    else:
        # Create new record if it doesn't exist
        data = {
            'type': record_type,
            'name': record_name,
            'content': content,
            'ttl': 1,
            'proxied': proxied
        }
        req = urllib.request.Request(base_url, data=json.dumps(data).encode(), headers=headers, method='POST')
    
    try:
        with urllib.request.urlopen(req) as response:
            if response.status in [200, 201]:
                logging.info(f"{record_type} record {'updated' if records else 'created'} successfully for {record_name}")
            else:
                logging.error(f"Failed to {'update' if records else 'create'} {record_type} record for {record_name}. Status code: {response.status}")
                logging.error(f"Response: {response.read().decode()}")
    except urllib.error.URLError as e:
        logging.error(f"Failed to {'update' if records else 'create'} record: {e}")



# Discover the absolute folder main.py is running on
main_py_path = os.path.dirname(os.path.abspath(__file__))
logging.info(f"main.py is running from: {main_py_path}")


# Read and process the input JSON file
with open(f"{main_py_path}/records.json", "r") as f:
    records = json.load(f)
    
# Get the current public IP address
try:
    with urllib.request.urlopen('https://api.ipify.org') as response:
        content = response.read().decode().strip()
except urllib.error.URLError as e:
    logging.error(f"Failed to get public IP: {e}")
    exit(1)

for record in records:
    # Get proxied value from JSON, default to True if not present
    proxied = record.get('proxied', True)
    
    update_record(record['record_name'], record['record_type'], content, proxied)