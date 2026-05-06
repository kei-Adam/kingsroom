import os
import time
import random
import logging
from datetime import datetime
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()
CITYHEAVEN_ID = os.getenv("CITYHEAVEN_ID")
CITYHEAVEN_PW = os.getenv("CITYHEAVEN_PW")
LOGIN_URL = os.getenv("LOGIN_URL", "http://newmanager.cityheaven.net/")

def debug_update():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        print(f"アクセス中: {LOGIN_URL}")
        page.goto(LOGIN_URL)
        
        page.locator('input[name="txt_account"]').filter(visible=True).fill(CITYHEAVEN_ID)
        page.locator('input[name="txt_password"]').filter(visible=True).fill(CITYHEAVEN_PW)
        page.locator('input[type="image"], button, input[type="submit"]').filter(visible=True).first.click()
        
        page.wait_for_load_state("networkidle")
        time.sleep(5)
        
        # ページ全体のボタン情報を出力
        buttons = page.locator('button, input[type="button"], input[type="submit"], a.btn, .btn, [role="button"]').all()
        print(f"発見されたボタン数: {len(buttons)}")
        for i, btn in enumerate(buttons):
            try:
                text = btn.inner_text().strip()
                visible = btn.is_visible()
                print(f"Button {i}: Text='{text}', Visible={visible}")
            except:
                pass
        
        # 「ヘブン更新ボタン」のコンテナを探す
        container = page.locator('div:has-text("ヘブン更新ボタン")').filter(visible=True).first
        if container.count() > 0:
            print("「ヘブン更新ボタン」のコンテナを発見。")
            update_btn = container.locator('text="更新"').filter(visible=True).first
            if update_btn.count() > 0:
                print("コンテナ内の「更新」ボタンを発見。クリックします。")
                update_btn.click()
                time.sleep(3)
                
                # ダイアログ（alert/confirm）が出ている可能性を考慮
                # Playwrightのデフォルトではダイアログは自動で閉じられるが、
                # 必要なら page.on("dialog", lambda dialog: dialog.accept()) を設定する
                
                print("クリック後のスクリーンショットを撮影します。")
                page.screenshot(path="debug_after_click.png")
            else:
                print("コンテナ内に「更新」ボタンが見つかりません。")
        else:
            print("「ヘブン更新ボタン」のコンテナが見つかりません。")
            
        browser.close()

if __name__ == "__main__":
    debug_update()
