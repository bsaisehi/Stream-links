import requests
import json
import time
import re

USER_AGENT = "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Mobile Safari/537.36"

SOURCES = {
    "cricfusion": {
        "base_url": "https://newwwwapiiiiii.vercel.app/main?id=",
        "items": ["cazeamzn", "h", "u", "fs1"],
        "type": "individual_id",
        "headers": {
            "Referer": "https://newwwwapiiiiii.vercel.app",
            "Origin": "https://cricfusion.pages.dev",
            "User-Agent": USER_AGENT
        }
    },
    "fifa26": {
        "base_url": "https://footballapi-delta.vercel.app/api/events?play=1",
        "items": [None],
        "type": "bulk_api",
        "headers": {
            "Origin": "https://fifa26-live.pages.dev",
            "User-Agent": USER_AGENT,
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9,hi;q=0.8"
        }
    }
}

def fetch_cricx_js():
    """Naye domain ki JS file se encrypted channel tokens nikalne ke liye"""
    url = "https://lchdxfootball.pages.dev/cricxfootball.js"
    headers = {"User-Agent": USER_AGENT, "Referer": "https://lchdxfootball.pages.dev/"}
    
    print("📡 Processing source: [CRICXFOOTBALL JS]")
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code in [200, 304] and res.text:
            # Regular Expression se 'encodedChannelData = { ... }' ke andar ka data dhoondhna
            match = re.search(r'const\s+encodedChannelData\s*=\s*(\{.*?\});', res.text, re.DOTALL)
            if match:
                js_object = match.group(1)
                
                # JS Object format ko clean karke proper JSON string me badalna
                # 1. Keys ke aas paas quotes lagana agar na hon
                clean_json = re.sub(r'(\b\w+\b)\s*:', r'"\1":', js_object)
                # 2. Last trailing comma hatana agar ho to
                clean_json = re.sub(r',\s*\}', '}', clean_json)
                # 3. Double quotes clean karna
                clean_json = clean_json.replace("'", '"')
                
                data = json.loads(clean_json)
                print(f"  ✅ Successfully extracted {len(data)} encrypted channels from JS file!")
                return data
            else:
                print("  ⚠️ Error: JS file me 'encodedChannelData' nahi mila.")
        else:
            print(f"  ❌ Failed to fetch JS file | Status Code: {res.status_code}")
    except Exception as e:
        print(f"  ⚠️ Error parsing JS file: {e}")
    return None

def fetch_all():
    master_list = {}
    print("🔄 Automation started... Fetching live streams data...\n")
    
    # 1. Purane APIs se data fetch karna
    for source_name, config in SOURCES.items():
        print(f"📡 Processing source: [{source_name.upper()}]")
        current_headers = config["headers"]
        
        for item in config["items"]:
            target_url = config["base_url"] if item is None else f"{config['base_url']}{item}"
            
            try:
                res = requests.get(target_url, headers=current_headers, timeout=10)
                if res.status_code in [200, 304] and res.text.strip():
                    try:
                        data = res.json()
                        if config["type"] == "bulk_api":
                            master_list[source_name] = data
                            print(f"  ✅ Successfully fetched ALL streams at once for {source_name}!")
                        else:
                            master_list[item] = data
                            print(f"  ✅ Successfully fetched ID: {item}")
                    except json.JSONDecodeError:
                        print(f"  ⚠️ Error: Got non-JSON response from {source_name}.")
                else:
                    print(f"  ❌ Failed to fetch {source_name} | Status Code: {res.status_code}")
            except Exception as e:
                print(f"  ⚠️ Connection Error: {e}")
                
            time.sleep(1)
        print("-" * 40)
        
    # 2. Naye CricXFootball JS se data nikal kar merge karna
    cricx_data = fetch_cricx_js()
    if cricx_data:
        master_list["cricxfootball_tokens"] = cricx_data
    print("-" * 40)
        
    # Final consolidated data save karna
    with open("all_streams.json", "w") as f:
        json.dump(master_list, f, indent=4)
        
    print(f"\n🎉 ALL DONE: Sara raw aur token data 'all_streams.json' me save ho chuka hai!")

if __name__ == "__main__":
    fetch_all()
