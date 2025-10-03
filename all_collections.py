import os
import time
import csv
import random
import re
import urllib.parse
from playwright.sync_api import sync_playwright
from datetime import datetime
# today
USER_DATA_DIR = r"C:\Users\Pushkar\playwright-steam-profile"
EXTENSION_PATH = r"C:\Users\Pushkar\AppData\Local\Google\Chrome\User Data\Default\Extensions\jjicbefpemnphinccgikpdaagjebbnhg\5.6.1_1"
HEADLESS = False

COLLECTIONS_BASE_FOLDER = r"C:\Users\Pushkar\OneDrive\Documents\Project\folders_for_html_sites\practial_with_onlyFNMWFT"
OUTPUT_BASE_FOLDER = r"C:\Users\Pushkar\OneDrive\Documents\Project\complete_using_python\Prices_csv\temp"

START_COLLECTION = "2018 Inferno Collection"  # Set to collection name to start from, or "" to start from the beginning


def extract_listings(page):
    listings = page.query_selector_all("div.market_listing_row")[1:]  # Skip the first row which is usually the header
    prices_and_floats = []
    for listing in listings:
        # Extract price
        price_elem = listing.query_selector(".market_listing_price_with_fee")
        price = price_elem.inner_text().strip() if price_elem else ""

        # Extract float (only the number)
        float_value = ""
        float_elem = listing.query_selector("span:has-text('Float:')")
        if float_elem:
            float_text = float_elem.inner_text().strip()
            match = re.search(r'Float:\s*([0-9.]+)', float_text)
            if match:
                float_value = match.group(1)
        prices_and_floats.append([price, float_value])
    return prices_and_floats
start_time = time.time()
start_collection_found = START_COLLECTION == ""

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        USER_DATA_DIR,
        headless=HEADLESS,
        args=[
            "--start-maximized",
            f"--disable-extensions-except={EXTENSION_PATH}",
            f"--load-extension={EXTENSION_PATH}"
        ],
        no_viewport=True
    )

    for collection_name in os.listdir(COLLECTIONS_BASE_FOLDER):
        collection_time=time.time()
        if not start_collection_found:
            if collection_name == START_COLLECTION:
                start_collection_found = True
            else:
                continue

        collection_path = os.path.join(COLLECTIONS_BASE_FOLDER, collection_name)
        if not os.path.isdir(collection_path):
            continue

        out_collection_folder = os.path.join(OUTPUT_BASE_FOLDER, collection_name.replace(" ", "_"))
        os.makedirs(out_collection_folder, exist_ok=True)

        for rarity_name in os.listdir(collection_path):
            rarity_path = os.path.join(collection_path, rarity_name)
            if not os.path.isdir(rarity_path):
                continue

            out_rarity_folder = os.path.join(out_collection_folder, rarity_name.replace(" ", "_"))
            os.makedirs(out_rarity_folder, exist_ok=True)

            for txt_filename in os.listdir(rarity_path):
                if not txt_filename.lower().endswith('.txt'):
                    continue

                skin_name = os.path.splitext(txt_filename)[0].replace(" ", "_").replace("-", "_")
                skin_folder = os.path.join(out_rarity_folder, skin_name)
                os.makedirs(skin_folder, exist_ok=True)

                txt_path = os.path.join(rarity_path, txt_filename)
                with open(txt_path, 'r', encoding='utf-8') as f:
                    links = [line.strip() for line in f if line.strip().startswith("http")]

                for TARGET_URL in links:
                    today= datetime.today().strftime("%d/%m/%Y")
                    now = datetime.now()
                    date_hour = now.strftime("%d/%m/%Y,%H:00")
                    max_retries = 10
                    min_delay = random.uniform(8,12)  # seconds
                    delay = min_delay
                    for attempt in range(1, max_retries + 1):
                        try:
                            page = browser.new_page()
                            #print(f"Visiting: {TARGET_URL} (Collection: {collection_name}, Rarity: {rarity_name}, Skin: {skin_name}) [Attempt {attempt}]")
                            page.goto(TARGET_URL, timeout=60000)
                            page.wait_for_selector("#market_commodity_buyrequests", timeout=30000)
                            page.wait_for_timeout(2000)

                            parsed_url = urllib.parse.unquote(TARGET_URL)
                            if "(" in parsed_url and ")" in parsed_url:
                                exterior = parsed_url.split("(")[-1].split(")")[0].strip().replace(" ", "_").lower()
                            else:
                                exterior = "unknown"
                            PRICES_CSV_PATH = os.path.join(skin_folder, f"{exterior}.csv")

                            buy_order_elems = page.query_selector_all("#market_commodity_buyrequests .market_commodity_orders_header_promote")
                            if len(buy_order_elems) >= 2:
                                buy_order_price = buy_order_elems[1].inner_text().strip()
                            else:
                                buy_order_price = ""
                            #print(f"Buy Order Price: {buy_order_price}")

                            max_wait = 30
                            float_start_time = time.time()
                            while True:
                                prices_and_floats = extract_listings(page)
    # PRIORITY: If 10 listings loaded, check last price and possibly retry


                                missing = [pf for pf in prices_and_floats if not pf[0] or not pf[1]]
                                if not missing:
                                    break
                                if time.time() - float_start_time > max_wait:
                                    print("Warning: Not all floats/prices loaded after waiting. Proceeding with available data.")
                                    break
                                time.sleep(random.uniform(0.5, 1.5))  # Random sleep to avoid being flagged as a bot
                            if not os.path.exists(PRICES_CSV_PATH):
    # Write new file as before
                                with open(PRICES_CSV_PATH, mode='w', newline='', encoding='utf-8') as f:
                                    writer = csv.writer(f)
                                    writer.writerow([date_hour, date_hour])
                                    writer.writerow(['price', 'float'])
                                    for price, float_value in prices_and_floats:
                                        writer.writerow([price, float_value])
                                    writer.writerow(['buy_order_price', buy_order_price])
                            else:
                                # Read existing data
                                with open(PRICES_CSV_PATH, mode='r', newline='', encoding='utf-8') as f:
                                    rows = list(csv.reader(f))

                                # Add new column to each row
                                # First row: date_hour
                                rows[0].extend([date_hour,date_hour])
                                # Second row: headers
                                rows[1].extend(['price', 'float'])

                                # Fill in new data for each row
                                data_len = len(prices_and_floats)
                                # For price/float rows
                                for i in range(2, 2 + data_len):
                                    if i < len(rows):
                                        rows[i].extend([prices_and_floats[i-2][0], prices_and_floats[i-2][1]])
                                    else:
                                        # If new run has more rows, add them
                                        rows.append([''] * (len(rows[0]) - 2) + [prices_and_floats[i-2][0], prices_and_floats[i-2][1]])
                                # For any extra old rows, just extend with blanks
                                for i in range(2 + data_len, len(rows) - 1):
                                    rows[i].extend(['', ''])
                                # Last row: buy_order_price
                                if len(rows) > 2 + data_len:
                                    rows[-1].extend(['buy_order_price', buy_order_price])
                                else:
                                    rows.append([''] * (len(rows[0]) - 2) + ['buy_order_price', buy_order_price])

                                # Write back to CSV
                                with open(PRICES_CSV_PATH, mode='w', newline='', encoding='utf-8') as f:
                                    writer = csv.writer(f)
                                    writer.writerows(rows)
                            time.sleep(random.uniform(1, 4))  # Random sleep to avoid being flagged as a bot
                            page.close()
                            delay = min_delay  # Reset delay after success
                            
                            break  # Success, break retry loop
                        except Exception as e:
                            print(f"[Attempt {attempt}] Failed at {collection_name} > {rarity_name} > {skin_name} > {TARGET_URL}")
                            print(f"Error: {e}")
                            if attempt == max_retries:
                                print(f"Giving up on {TARGET_URL} after {max_retries} attempts.")
                            else:
                                print(f"Retrying in {delay} seconds...")
                                time.sleep(delay)
                                delay += random.uniform(50,100)  # Increase delay by 200s for next retry
                            if 'page' in locals():
                                try:
                                    page.close()
                                except:
                                    pass
        print(f"Collection '{collection_name}' processed in {time.time() - collection_time:.2f} seconds.")                                
    browser.close()
print(f"Total execution time: {time.time() - start_time:.2f} seconds")