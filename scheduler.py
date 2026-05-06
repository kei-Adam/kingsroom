import schedule
import time
import logging
import subprocess
import sys
from datetime import datetime

# ログの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scheduler.log"),
        logging.StreamHandler()
    ]
)

def job():
    logging.info("ジョブを開始します: cityheaven_updater.py を実行中...")
    try:
        # 外部プロセスとして実行し、結果を待つ
        result = subprocess.run([sys.executable, "cityheaven_updater.py"], capture_output=True, text=True)
        logging.info(f"実行完了。出力:\n{result.stdout}")
        if result.stderr:
            logging.error(f"エラー出力:\n{result.stderr}")
    except Exception as e:
        logging.error(f"ジョブ実行中にエラーが発生しました: {e}")

# 実行スケジュールの設定
# 深夜帯（4回 / 1時間間隔）
late_night_times = ["00:15", "01:15", "02:15", "03:15"]
# 日中帯（8回 / 1時間間隔）
day_times = ["11:15", "12:15", "13:15", "14:15", "15:15", "16:15", "17:15", "18:15"]
# 夜間ピーク帯（11回 / 30分間隔）
peak_times = [
    "18:45", "19:15", "19:45", "20:15", "20:45", 
    "21:15", "21:45", "22:15", "22:45", "23:15", "23:45"
]

all_times = late_night_times + day_times + peak_times

for t in all_times:
    schedule.every().day.at(t).do(job)
    logging.info(f"スケジュール登録: {t}")

logging.info(f"スケジューラを起動しました。合計 {len(all_times)} 回の実行が予約されています。")

if __name__ == "__main__":
    # 初回実行チェック用（デバッグ時にコメントを外す）
    # job()
    
    while True:
        schedule.run_pending()
        time.sleep(60) # 1分ごとにチェック
