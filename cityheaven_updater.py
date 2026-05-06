import os
import time
import random
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

# 設定の読み込み
load_dotenv()
CITYHEAVEN_ID = os.getenv("CITYHEAVEN_ID")
CITYHEAVEN_PW = os.getenv("CITYHEAVEN_PW")
LOGIN_URL = os.getenv("LOGIN_URL", "http://newmanager.cityheaven.net/")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID = os.getenv("LINE_USER_ID")

# ログの設定
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
        logging.warning("LINE_CHANNEL_ACCESS_TOKEN または LINE_USER_ID が設定されていません。LINE通知はスキップされます。")
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
            logging.info("LINEに通知を送信しました。")
        else:
            logging.error(f"LINE通知の送信に失敗しました: {response.status_code} - {response.text}")
    except Exception as e:
        logging.error(f"LINE通知の送信中にエラーが発生しました: {e}")

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
                
                logging.info(f"アクセス中: {LOGIN_URL}")
                page.goto(LOGIN_URL)
                page.wait_for_load_state("networkidle")
                
                # ヒューマンライク・ディレイ
                time.sleep(random.uniform(2, 5))
                
                # ログイン処理
                logging.info("ログイン情報を入力中...")
                page.locator('input[name="txt_account"]').filter(visible=True).fill(CITYHEAVEN_ID)
                page.locator('input[name="txt_password"]').filter(visible=True).fill(CITYHEAVEN_PW)
                
                time.sleep(random.uniform(1, 3))
                
                # ログインボタンをクリック
                login_button = page.locator('input[type="image"], button, input[type="submit"]').filter(visible=True).first
                login_button.click()
                
                logging.info("ログイン中...")
                page.wait_for_load_state("networkidle")
                
                # ログイン後のページ確認
                time.sleep(random.uniform(3, 6))
                
                # 更新ボタンを探す
                logging.info("更新ボタンを探索中...")
                
                # ダイアログ（確認画面）を自動的に承認するように設定
                page.on("dialog", lambda dialog: (logging.info(f"ダイアログを承認: {dialog.message}"), dialog.accept()))
                
                # 1. 「ヘブン更新ボタン」というテキストを含むカード/コンテナを探す
                # 2. その中の「更新」ボタンをクリックする
                # もしくはトップレベルの「更新」ボタンを探す
                
                update_button = None
                
                # コンテナベースの探索
                container = page.locator('div, a, button').filter(has_text="ヘブン更新ボタン").filter(visible=True).first
                if container.count() > 0:
                    # コンテナ内の「更新」というテキストを持つ要素を探す
                    btn_in_container = container.locator('text="更新"').filter(visible=True).first
                    if btn_in_container.count() > 0:
                        update_button = btn_in_container
                        logging.info("コンテナ内の更新ボタンを特定しました。")
                
                # 見つからない場合は直接探索
                if not update_button:
                    selectors = [
                        'button:has-text("更新")',
                        'a:has-text("更新")',
                        'input[value="更新"]',
                        'text="更新"'
                    ]
                    for selector in selectors:
                        try:
                            loc = page.locator(selector).filter(visible=True).first
                            if loc.count() > 0:
                                update_button = loc
                                logging.info(f"直接探索でボタンを特定しました: {selector}")
                                break
                        except:
                            continue
                
                if update_button:
                    # 要素がクリック可能になるまで待機
                    update_button.scroll_into_view_if_needed()
                    time.sleep(random.uniform(1, 2))
                    
                    logging.info("更新ボタンをクリックします。")
                    update_button.click()
                    
                    # クリック後に少し待機して、ページの変化を確認
                    logging.info("処理完了を待機中...")
                    page.wait_for_load_state("networkidle")
                    time.sleep(random.uniform(5, 8))
                    
                    logging.info("更新処理を完了しました。結果を確認します。")
                    
                    # 完了のスクリーンショット
                    now_str = datetime.now().strftime('%Y%m%d_%H%M%S')
                    page.screenshot(path=f"screenshots/result_{now_str}.png")
                    
                    # 更新時間が変わったかどうかのログ出力（オプション）
                    new_time_text = ""
                    try:
                        new_time_text = page.locator('text="最終更新日時"').first.inner_text()
                        logging.info(f"現在の画面表示: {new_time_text}")
                    except:
                        pass
                    
                    browser.close()
                    
                    # LINE通知
                    msg = f"✅ 自動更新に成功しました。\n時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    if new_time_text:
                        msg += f"\n{new_time_text}"
                    send_line_message(msg)
                    
                    return True
                else:
                    logging.warning("更新ボタンが見つかりませんでした。")
                    page.screenshot(path=f"screenshots/error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                    browser.close()
                    send_line_message(f"❌ 更新ボタンが見つかりませんでした。\n時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    return False
                    
        except Exception as e:
            logging.error(f"エラーが発生しました (試行 {retry_count + 1}/{max_retries}): {e}")
            retry_count += 1
            if retry_count < max_retries:
                wait_time = 300 # 5分
                logging.info(f"{wait_time}秒後にリトライします...")
                time.sleep(wait_time)
            else:
                logging.error("最大リトライ回数に達しました。")
                send_line_message(f"🚨 最大リトライ回数に達し、処理を終了しました。\n時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                return False

if __name__ == "__main__":
    if not os.path.exists("screenshots"):
        os.makedirs("screenshots")
    run_update()
