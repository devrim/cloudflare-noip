import requests
import json
import os
import logging
from logging.handlers import RotatingFileHandler

# Set up logging with rotation
log_file = '/tmp/cloudflare-noip.log'
max_log_size = 1 * 1024 * 1024  # 1 MB
backup_count = 3  # Keep 3 old log files

handler = RotatingFileHandler(log_file, maxBytes=max_log_size, backupCount=backup_count)
formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# Read Cloudflare credentials
credentials_path = os.path.expanduser('~/.cloudflare-noip/keys.json')
if not os.path.exists(credentials_path):
    logger.info("Error: The file ~/.cloudflare-noip/keys.json does not exist.")
    logger.info("Please create the folder ~/.cloudflare-noip/keys.json with the following structure:")
    logger.info('''{
    "api_key": "your_cloudflare_api_key",
    "email": "your_cloudflare_email",
    "zone_id": "your_cloudflare_zone_id", // deprecated, use zone_ids instead
    "zone_ids": {
        "website_name": "zone_id",
        "website_name2": "zone_id2",
        "website_name3": "zone_id3"
    }
    }''')
    exit(1)
    
with open(credentials_path, 'r') as f:
    credentials = json.load(f)


API_KEY = credentials['api_key']
EMAIL = credentials['email']
ZONE_ID = credentials['zone_id'] if 'zone_id' in credentials else None
ZONE_IDS = credentials['zone_ids'] if 'zone_ids' in credentials else {}
    
IP_FILE_PATH = '~/.cloudflare-noip/IP.txt'  
RECORDS_FILE_PATH = '~/.cloudflare-noip/records.json'


def get_base_url(website_name=""):

    if website_name in ZONE_IDS:
        return f'https://api.cloudflare.com/client/v4/zones/{ZONE_IDS[website_name]}/dns_records'
    else:
        logger.info(f"Error: Website {website_name} not found in zone_ids, using default zone_id")
        return f'https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records'
        
        


# Headers for authentication
headers = {
    'X-Auth-Email': EMAIL,
    'X-Auth-Key': API_KEY,
    'Content-Type': 'application/json'
}

def update_records(new_ip):
    # Read and process the input JSON file
    with open(RECORDS_FILE_PATH, "r") as f:
        records = json.load(f)
    
    for record in records:    
    # Get proxied value from JSON, default to True if not present
        proxied = record.get('proxied', True)
    
        website_name = record.get('website_name', '')  # Get website_name from record, default to empty string
        update_record(record['record_name'], record['record_type'], new_ip, proxied, website_name)
        

def update_record(record_name, record_type, content, proxied=True, website_name=''):
    base_url = get_base_url(website_name)
    # Find the existing record
    response = requests.get(base_url, headers=headers, params={'name': record_name, 'type': record_type})
    if not response.json()['success']:
        logger.info(response.json())
        logger.info(f"Error: {response.json()['errors'][0]['message']}")
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
        logger.info(f"{record_type} record {'updated' if records else 'created'} successfully for {record_name}")
    else:
        logger.info(f"Failed to {'update' if records else 'create'} {record_type} record for {record_name}. Status code: {response.status_code}")
        logger.info(response.text)


def write_ip_to_file(ip):
    ip_file_path = os.path.expanduser(IP_FILE_PATH)
    os.makedirs(os.path.dirname(ip_file_path), exist_ok=True)
    with open(ip_file_path, 'w') as ip_file:
        ip_file.write(ip)
    logger.info(f"Current IP written to {ip_file_path}")
    
def read_ip_from_file():
    ip_file_path = os.path.expanduser(IP_FILE_PATH)
    if os.path.exists(ip_file_path):
        with open(ip_file_path, 'r') as ip_file:
            return ip_file.read().strip()
    else:
        logger.info("IP file does not exist")
        logger.info("Creating empty IP file")
        with open(ip_file_path, 'w') as ip_file:
            pass
        return None


def main():
    # Get the current public IP address
    try:
        response = requests.get('https://api.ipify.org')
        new_ip = response.text.strip()
        
        # Write the current IP to a file
        old_ip = read_ip_from_file()

        # Check if the IP has changed
        if old_ip != new_ip:
            logger.info("IP changed")
            update_records(new_ip)
            write_ip_to_file(new_ip)
        else:
            logger.info("IP is the same as before, not taking any action")
        
        
        # logger.info(f"Current public IP: {content}")  # Uncomment if you want to log this
    except requests.RequestException as e:
        logger.info(f"Failed to get public IP: {e}")
        exit(1)


if __name__ == "__main__":
    import time
    
    logger.info("Starting cloudflare-noip, this is setup to run every second for 60 seconds, you should set up your cron job to run this every minute")
    
    count = 0
    while count < 60:
        main()
        time.sleep(1)
        count += 1
