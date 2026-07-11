import json
import time
from playwright.sync_api import sync_playwright

# Aapka target URL
TARGET_URL = "https://streamcorner.foo/stream/fifa/02e0da44-e81a-54c6-939d-12d2e579abd5"

def scrape_streams():
    data = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print(f"Loading page: {TARGET_URL}")
        page.goto(TARGET_URL, wait_until="networkidle")
        time.sleep(5) # Page fully load hone dein

        # 1. HACK: Piche chalne wale ad overlays ko page se uadana
        page.evaluate("""() => {
            const overlay = document.getElementById('dontfoid');
            if (overlay) {
                overlay.remove();
                console.log('Ad overlay removed successfully.');
            }
            // Agar koi aur transparent full-screen div ho toh use bhi clear karein pointer events se
            document.querySelectorAll('div').forEach(div => {
                if (window.getComputedStyle(div).position === 'fixed' && window.getComputedStyle(div).zIndex > 999) {
                    div.remove();
                }
            });
        }""")

        # Saare buttons list fetch karna
        buttons = page.query_selector_all("button.stream-source-btn")
        total_buttons = len(buttons)
        print(f"Found {total_buttons} channels.")

        for index, btn in enumerate(buttons):
            channel_id = index + 1
            try:
                # Channel Name nikalna
                name_el = btn.query_selector("span.truncate")
                channel_name = name_el.inner_text().strip() if name_el else f"Channel {channel_id}"
                
                print(f"Scraping ({channel_id}/{total_buttons}): {channel_name}")
                
                # 2. HACK: Standard click ke bajaye JS se DIRECT CLICK bypass apply karna
                # Isse pointer-intercept error hamesha ke liye khatam ho jayega
                page.evaluate("(element) => element.click()", btn)
                time.sleep(2.5) # Iframe src update hone ka fast wait

                # Player Iframe ka selector check karna
                iframe_element = page.query_selector("iframe[title], .player-section iframe, .app-container iframe")
                
                if iframe_element:
                    iframe_src = iframe_element.get_attribute("src")
                    if iframe_src:
                        data.append({
                            "id": channel_id,
                            "name": channel_name,
                            "url": iframe_src
                        })
                        print(f"-> Success: {iframe_src[:50]}...")
                else:
                    print(f"-> Warning: Could not find iframe for {channel_name}")
                    
            except Exception as e:
                print(f"-> Error scraping channel {channel_id}: {e}")
                continue
                
        browser.close()

    # JSON output save karna
    with open("streams.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print(f"Scraping completed! Total {len(data)} channels saved in streams.json")

if __name__ == "__main__":
    scrape_streams()
