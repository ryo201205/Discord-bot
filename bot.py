from flask import Flask
import threading
import discord
import gspread
import os
import re
import json
from datetime import datetime
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2.service_account import Credentials

# ------------------ Health Check Flask ------------------
app = Flask(__name__)

@app.route("/health")
def health():
    return "ok", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))  # ← ここでPORTをRenderに合わせる
    app.run(host="0.0.0.0", port=port)

flask_thread = threading.Thread(target=run_flask)
flask_thread.start()

# ------------------ 初期設定 ------------------
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
SPREADSHEET_NAME = "StCi警察経費申請管理"
TARGET_CHANNEL_NAME = "経費申請"

# ------------------ Discord Bot 設定 ------------------
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# ------------------ Google Sheets 認証 ------------------
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials_info = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_info, scope)
gc = gspread.authorize(credentials)
sheet = gc.open(SPREADSHEET_NAME).sheet1

# ------------------ メッセージ処理 ------------------
@client.event
async def on_ready():
    print(f"✅ Botログイン成功！ユーザー: {client.user}")

@client.event
async def on_message(message):
    if message.author.bot:
        return
    if message.channel.name != TARGET_CHANNEL_NAME:
        return
    if re.fullmatch(r"\d+", message.content.strip()):
        金額 = int(message.content.strip())
        表示名 = message.author.display_name
        日付 = datetime.now().strftime('%Y/%m/%d %H:%M')
        data = sheet.get_all_records()
        updated = False
        for i, row in enumerate(data, start=2):
            if row['ユーザー'] == 表示名:
                新しい金額 = int(row['金額']) + 金額
                sheet.update_cell(i, 2, 新しい金額)
                sheet.update_cell(i, 3, 日付)
                updated = True
                break
        if not updated:
            sheet.append_row([表示名, 金額, 日付])
        await message.add_reaction("✅")

# ------------------ Bot起動 ------------------
client.run(DISCORD_TOKEN)
