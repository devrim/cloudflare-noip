# Cloudflare NoIP Alternative

This project provides a free alternative to paid dynamic DNS services like NoIP.com. It allows you to update your DNS records on Cloudflare automatically using a free Cloudflare account and a cronjob on your computer.

## Setup

1. Clone this repository to your local machine.

2. Create a `keys.json` file in the `~/.cloudflare-noip/` directory with the following structure:

```json
{
    "api_key": "your_cloudflare_api_key",
    "email": "your_cloudflare_email",
    "zone_id": "your_cloudflare_zone_id"
}
```

To get your Cloudflare API key and zone ID:

- Log in to your Cloudflare account and go to the "My Profile" section.
- Click on "API Tokens" and create a new token with the "Zone" permission.
- Copy the API key and zone ID from the token details.

3. Create a `records.json` file in the `~/.cloudflare-noip/` directory with the following structure:

```json
[
    {
        "type": "A",
        "name": "your_subdomain"
    }
]
```

The `content` field will be automatically updated with the IP address of the machine running the script.

4. Set up a cronjob to run the script at the desired interval. Here are examples for Ubuntu, macOS, and Windows:

**Ubuntu/Debian:**

```bash
crontab -e
```

Add the following line to run the script every 5 minutes:

```bash
*/60 * * * * cd /path/to/cloudflare-noip && /usr/bin/python3 main.py
```

**macOS (using launchd):**

1. Create a new file in `~/Library/LaunchAgents/` called `com.example.cloudflare-noip.plist` with the following contents:

below should work but it doesn't let me know if you have any pointers.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key>
    <string>com.example.cloudflare-noip</string>
    <key>ProgramArguments</key>
    <array>
      <string>python</string>
      <string>/path/to/cloudflare_noip.py</string>
    </array>
    <key>StartInterval</key>
    <dict>
      <key>Interval</key>
      <integer>300</integer>
    </dict>
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
	* Triggers: Create a new trigger with the desired interval (e.g., every 5 minutes).
	* Actions: Create a new action to start a program: `python.exe` with the argument `/path/to/cloudflare_noip.py`.
	* Conditions: Set any additional conditions as needed.
3. Save the task.

The script will update the DNS records on Cloudflare with the current IP address of the machine running the script at the specified interval.
