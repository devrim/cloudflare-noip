# Cloudflare NoIP Alternative

This project provides a free alternative to paid dynamic DNS services like NoIP.com. It allows you to update your DNS records on Cloudflare automatically using a free Cloudflare account and a cronjob on your computer.

## Setup

1. Clone this repository to your local machine.

2. Create a `keys.json` file in the `~/.cloudflare-noip/` directory with the following structure:

```json
{
    "api_key": "your_cloudflare_api_key",
    "email": "your_cloudflare_email",
    "zone_ids": {
		  "website_name1":"cloudflare_zone_id1",
		  "website_name2":"cloudflare_zone_id2"
		}
}
```

To get your Cloudflare API key and zone ID:

- Log in to your Cloudflare account and go to the "My Profile" section.
- Click on "API Tokens" and create a new token with the template " Edit zone DNS" permission.
- Go to your website overview page, on the bottom right you'll see Zone ID, copy that and paste in to your keys.json

3. Create a `records.json` file in the `~/.cloudflare-noip/` directory with the following structure:

```json
[
	{
        "record_name": "sub.domain.xyz",
        "record_type": "A",
        "proxied": true
		"website_name": "domain.xyz"
	},
	{
	    "record_name": "sub.domain1.xyz",
        "record_type": "A",
        "proxied": true
		"website_name": "domain1.xyz"
	}
]
```

The `content` field will be automatically updated with the IP address of the machine running the script.

4. Set up a cronjob to run the script at the desired interval. Here are examples for Ubuntu, macOS, and Windows:

**Ubuntu/Debian:**

```bash
crontab -e
```

Add the following line to run the script every minute, this script will run every second for 60 times.
(one HN user rightly pointed out that since it's a home server 1 second update is more appropriate; this frequency is your max downtime. Update: from this version onwards, this program will only update Cloudflare if IP changes.)

```bash
*/1 * * * * cd /path/to/cloudflare-noip && /usr/bin/python3 main.py
```

restart cron (optional)
```bash
sudo systemctl restart cron
```

**macOS (using launchd):**

1. Create a new file in `~/Library/LaunchAgents/` called `com.example.cloudflare-noip.plist` with the following contents:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>Label</key>
	<string>com.example.cloudflare-noip</string>
	<key>ProgramArguments</key>
	<array>
		<string>/usr/bin/python3</string>
		<string>/Users/d/Projects/cloudflare-noip/main.py</string>
	</array>
	<key>StartInterval</key>
	<integer>60</integer>
</dict>
</plist>
```

2. Load the launch agent:

```bash
launchctl load ~/Library/LaunchAgents/com.example.cloudflare-noip.plist
```

**Windows (using Task Scheduler):**

1. Open the Task Scheduler: Press the Windows key + R, type `taskschd.msc`, and press Enter.
2. Create a new task:
	* General: Give the task a name and description.
	* Triggers: Create a new trigger with the desired interval (e.g., every minute).
	* Actions: Create a new action to start a program: `python.exe` with the argument `/path/to/cloudflare_noip.py`.
	* Conditions: Set any additional conditions as needed.
3. Save the task.

The script will update the DNS records on Cloudflare with the current IP address of the machine running the script at the specified interval.
