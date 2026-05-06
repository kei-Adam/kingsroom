#!/bin/bash
# スクリプトがあるディレクトリに移動
cd "$(dirname "$0")"

echo "=========================================="
echo "  シティヘブン自動更新ツール 起動メニュー"
echo "=========================================="
echo "初回起動時や別Macでの実行時は、必要な設定の確認を行います..."

# 必要なパッケージのインストールチェック（エラーを出さずに静かに実行）
pip3 install -r requirements.txt -q
playwright install chromium -q

echo ""
echo "1. スケジューラを起動する (1日23回自動実行)"
echo "2. 今すぐ1回だけ更新する (手動実行)"
echo "3. デバッグ実行"
echo "=========================================="
read -p "実行する番号を選んでEnterを押してください: " num

if [ "$num" = "1" ]; then
    echo ""
    echo "スケジューラを起動します。"
    echo "※ 自動更新を続けるため、この黒いウィンドウは開いたままにしてください。"
    echo "------------------------------------------"
    python3 scheduler.py
elif [ "$num" = "2" ]; then
    echo ""
    echo "今すぐ1回だけ更新を実行します。"
    echo "------------------------------------------"
    python3 cityheaven_updater.py
elif [ "$num" = "3" ]; then
    echo ""
    echo "デバッグ実行を開始します。"
    echo "------------------------------------------"
    python3 debug_update.py
else
    echo "無効な入力です。"
fi

echo ""
echo "処理が終了しました。Enterを押してウィンドウを閉じてください。"
read
