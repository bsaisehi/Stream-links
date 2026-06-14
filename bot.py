import requests
import json
import time

USER_AGENT = "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Mobile Safari/537.36"

# Sabhi sources ke sahi backend aur headers ka configuration
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
        # Yeh tumhara dhoondha hua asli backend hai jo sabhi streams ek sath dega
        "base_url": "https://footballapi-delta.vercel.app/api/events?play=1",
        "items": [None], # Isme alag se loop chalane ki need nahi hai, ek hi call me sab aayega
        "type": "bulk_api",
        "headers": {
            "Origin": "https://fifa26-live.pages.dev",
            "User-Agent": USER_AGENT,
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9,hi;q=0.8"
        }
    }
}

def fetch_all():
    master_list = {}
    print("🔄 Automation started... Fetching live streams data...\n")
    
    for source_name, config in SOURCES.items():
        print(f"📡 Processing source: [{source_name.upper()}]")
        current_headers = config["headers"]
        
        for item in config["items"]:
            # URL banana (bulk api ke liye item None hoga isliye direct url use hoga)
            target_url = config["base_url"] if item is None else f"{config['base_url']}{item}"
            
            try:
                res = requests.get(target_url, headers=current_headers, timeout=10)
                
                if res.status_code == 200 and res.text.strip():
                    try:
                        data = res.json()
                        
                        # Agar bulk list dene wali API hai (jaise FIFA26)
                        if config["type"] == "bulk_api":
                            master_list[source_name] = data
                            print(f"  ✅ Successfully fetched ALL streams at once for {source_name}!")
                        
                        # Agar ek ek karke ID fetch karne wali API hai (jaise Cricfusion)
                        else:
                            master_list[item] = data
                            print(f"  ✅ Successfully fetched ID: {item}")
                            
                    except json.JSONDecodeError:
                        print(f"  ⚠️ Error: Got non-JSON response from server.")
                else:
                    print(f"  ❌ Failed to fetch | Status Code: {res.status_code}")
                    
            except Exception as e:
                print(f"  ⚠️ Connection Error: {e}")
                
            # Rate limit se bachne ke liye chhota sa pause
            time.sleep(1.5)
            
        print("-" * 40)
        
    # Final consolidated data save karna
    with open("all_streams.json", "w") as f:
        json.dump(master_list, f, indent=4)
        
    print(f"\n🎉 Process finished! Data successfully saved in 'all_streams.json'.")

if __name__ == "__main__":
    fetch_all()
