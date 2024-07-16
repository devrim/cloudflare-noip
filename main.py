import requests
import json
import os

# Read Cloudflare credentials
credentials_path = os.path.expanduser('~/.cloudflare-noip/keys.json')
if not os.path.exists(credentials_path):
    print("Error: The file ~/.cloudflare-noip/keys.json does not exist.")
    print("Please create the folder ~/.cloudflare-noip/keys.json with the following structure:")
    print('''{
    "api_key": "your_cloudflare_api_key",
    "email": "your_cloudflare_email",
    "zone_id": "your_cloudflare_zone_id"
}''')
    exit(1)
    
with open(credentials_path, 'r') as f:
    credentials = json.load(f)

print(credentials)

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
    response = requests.get(base_url, headers=headers, params={'name': record_name, 'type': record_type})
    if not response.json()['success']:
        print(response.json())
        print(f"Error: {response.json()['errors'][0]['message']}")
        exit(1)
    
    records = response.json()['result']
    
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
        response = requests.put(update_url, headers=headers, json=data)
    else:
        # Create new record if it doesn't exist
        data = {
            'type': record_type,
            'name': record_name,
            'content': content,
            'ttl': 1,
            'proxied': proxied
        }
        response = requests.post(base_url, headers=headers, json=data)
    
    if response.status_code in [200, 201]:
        print(f"{record_type} record {'updated' if records else 'created'} successfully for {record_name}")
    else:
        print(f"Failed to {'update' if records else 'create'} {record_type} record for {record_name}. Status code: {response.status_code}")
        print(response.text)

# Read and process the input JSON file
with open("records.json", "r") as f:
    records = json.load(f)

for record in records:
    
    # Get the current public IP address
    try:
        response = requests.get('https://api.ipify.org')
        content = response.text.strip()
        # print(f"Current public IP: {content}")
    except requests.RequestException as e:
        print(f"Failed to get public IP: {e}")
        exit(1)
    
    # Get proxied value from JSON, default to True if not present
    proxied = record.get('proxied', True)
    
    update_record(record['record_name'], record['record_type'], content, proxied)