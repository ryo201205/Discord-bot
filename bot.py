import discord
import gspread
import os
import re
from datetime import datetime
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials

# ------------------ 初期設定 ------------------
load_dotenv()  # .envファイルから環境変数を読み込む

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
SPREADSHEET_NAME = "StCi警察経費申請管理"  # 必要に応じて変更
TARGET_CHANNEL_NAME = "経費申請"  # 経費申請を受け付けるチャンネル名

# ------------------ Discord Bot 設定 ------------------
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# ------------------ Google Sheets 認証 ------------------
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
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

        # 全データを取得しユーザーがいるかチェック
        data = sheet.get_all_records()
        updated = False

        for i, row in enumerate(data, start=2):  # ヘッダーを除く
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
