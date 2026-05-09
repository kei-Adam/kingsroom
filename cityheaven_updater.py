import os
import time
import random
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

# Load settings
load_dotenv()
CITYHEAVEN_ID = os.getenv("CITYHEAVEN_ID")
CITYHEAVEN_PW = os.getenv("CITYHEAVEN_PW")
LOGIN_URL = os.getenv("LOGIN_URL", "http://newmanager.cityheaven.net/")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID = os.getenv("LINE_USER_ID")

# Logging configuration
logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
                    logging.FileHandler("app.log"),
                    logging.StreamHandler()
        ]
)

def send_line_message(message):
        if not LINE_CHANNEL_ACCESS_TOKEN or not LINE_USER_ID:
                    logging.warning("LINE_CHANNEL_ACCESS_TOKEN or LINE_USER_ID is not set.")
                    return

        url = "https://api.line.me/v2/bot/message/push"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
        }
        data = {
            "to": LINE_USER_ID,
            "messages": [{"type": "text", "text": message.strip()}]
        }

    try:
                response = requests.post(url, headers=headers, json=data)
                if response.status_code == 200:
                                logging.info("LINE notification sent.")
    else:
            logging.error(f"Failed to send LINE notification: {response.status_code} - {response.text}")
    except Exception as e:
        logging.error(f"Error sending LINE notification: {e}")

def run_update():
        max_retries = 3
        retry_count = 0

    while retry_count < max_retries:
                try:
                                with sync_playwright() as p:
                                                    browser = p.chromium.launch(headless=True)
                                                    context = browser.new_context(
                                                        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                                                    )
                                                    page = context.new_page()

                logging.info(f"Accessing: {LOGIN_URL}")
                        page.goto(LOGIN_URL)
                page.wait_for_load_state("networkidle")

                # Human-like delay
                time.sleep(random.uniform(2, 5))

                # Login process
                logging.info("Inputting login info...")
                page.locator('input[name="txt_account"]').filter(visible=True).fill(CITYHEAVEN_ID)
                page.locator('input[name="txt_password"]').filter(visible=True).fill(CITYHEAVEN_PW)

                time.sleep(random.uniform(1, 3))

                # Click login button
                login_button = page.locator('input[type="image"], button, input[type="submit"]').filter(visible=True).first
                login_button.click()

                logging.info("Logging in...")
                page.wait_for_load_state("networkidle")

                # Post-login wait
                time.sleep(random.uniform(3, 6))

                # Search for update button
                logging.info("Searching for update button...")

                # Auto-accept dialogs
                page.on("dialog", lambda dialog: (logging.info(f"Accepting dialog: {dialog.message}"), dialog.accept()))

                update_button = None

                # Search by container
                container_text = "\u30d8\u30d6\u30f3\u66f4\u65b0\u30dc\u30bf\u30f3" 
                container = page.locator('div, a, button').filter(has_text=container_text).filter(visible=True).first
                if container.count() > 0:
                                        btn_text = "\u66f4\u65b0"
                                        btn_in_container = container.locator(f'text="{btn_text}"').filter(visible=True).first
                                        if btn_in_container.count() > 0:
                                                                    update_button = btn_in_container
                                                                    logging.info("Found update button in container.")

                                    # Direct search if not found
                                    if not update_button:
                                                            btn_text = "\u66f4\u65b0"
                                                            selectors = [
                                                                f'button:has-text("{btn_text}")',
                                                                f'a:has-text("{btn_text}")',
                                                                f'input[value="{btn_text}"]',
                                                                f'text="{btn_text}"'
                                                            ]
                                                            for selector in selectors:
                                                                                        try:
                                                                                                                        loc = page.locator(selector).filter(visible=True).first
                                                                                                                        if loc.count() > 0:
                                                                                                                                                            update_button = loc
                                                                                                                                                            logging.info(f"Found update button by selector: {selector}")
                                                                                                                                                            break
                                                                                                                                                    except:
                                                                                                                        continue

                if update_button:
                                        update_button.scroll_into_view_if_needed()
                    time.sleep(random.uniform(1, 2))

                    logging.info("Clicking update button.")
                    update_button.click()

                    logging.info("Waiting for completion...")
                    page.wait_for_load_state("networkidle")
                    time.sleep(random.uniform(5, 8))

                    logging.info("Update complete. Checking result.")

                    # Screenshot
                    now_str = datetime.now().strftime('%Y%m%d_%H%M%S')
                    page.screenshot(path=f"screenshots/result_{now_str}.png")

                    # Log last update time if found
                    status_text = "\u6700\u7d42\u66f4\u65b0\u65e5\u6642"
                    new_time_text = ""
                    try:
                                                new_time_text = page.locator(f'text="{status_text}"').first.inner_text()
                        logging.info(f"Status: {new_time_text}")
                    except:
                        pass

                    browser.close()

                    # LINE notification
                    success_msg = f"\u2705 Update Successful.\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    if new_time_text:
                                                success_msg += f"\n{new_time_text}"
                    send_line_message(success_msg)

                    return True
else:
                    logging.warning("Update button not found.")
                    page.screenshot(path=f"screenshots/error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                    browser.close()
                    fail_msg = f"\u274c Update button not found.\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    send_line_message(fail_msg)
                    return False

except Exception as e:
            logging.error(f"Error occurred (Try {retry_count + 1}/{max_retries}): {e}")
            retry_count += 1
            if retry_count < max_retries:
                                wait_time = 300
                logging.info(f"Retrying in {wait_time}s...")
                time.sleep(wait_time)
else:
                logging.error("Max retries reached.")
                error_msg = f"\ud83d\udea8 Max retries reached.\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                send_line_message(error_msg)
                return False

if __name__ == "__main__":
        if not os.path.exists("screenshots"):
                    os.makedirs("screenshots")
    run_update()
