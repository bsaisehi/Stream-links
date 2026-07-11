import json
import time
from playwright.sync_api import sync_playwright

# Yahan apni target website ka URL dalein
TARGET_URL = "https://streamcorner.foo/stream/fifa/02e0da44-e81a-54c6-939d-12d2e579abd5"

def scrape_streams():
    data = []
    
    with sync_playwright() as p:
        # Browser ko headless mode me chalana (GitHub Actions ke liye zaroori)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print(f"Loading page: {TARGET_URL}")
        page.goto(TARGET_URL, wait_until="networkidle")
        time.sleep(5) # Page ko poori tarah load hone ka time dena

        # Saare stream buttons ko dhoondhna unki class ke hisab se
        buttons = page.query_selector_all("button.stream-source-btn")
        print(f"Found {len(buttons)} channels.")

        for index, btn in enumerate(buttons):
            try:
                # Channel ka naam nikalna
                channel_name = btn.query_selector("span.truncate").inner_text().strip()
                channel_id = index + 1
                
                print(f"Scraping ({channel_id}/{len(buttons)}): {channel_name}")
                
                # Button par click karna taaki iframe update ho
                btn.click()
                time.sleep(3) # Iframe src change hone ka wait karna
                
                # Naye iframe ka src URL nikalna
                # (Aapke bataye mutabik player shaka ya main stream area ka selector)
                iframe_element = page.query_selector("div.player-section iframe, iframe[title]")
                
                if iframe_element:
                    iframe_src = iframe_element.get_attribute("src")
                    
                    # Object me data save karna
                    data.append({
                        "id": channel_id,
                        "name": channel_name,
                        "url": iframe_src
                    })
                else:
                    print(f"Could not find iframe for {channel_name}")
                    
            except Exception as e:
                print(f"Error scraping button {index+1}: {e}")
                continue
                
        browser.close()

    # Data ko streams.json me save karna
    with open("streams.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print("Scraping completed! streams.json saved.")

if __name__ == "__main__":
    scrape_streams()
