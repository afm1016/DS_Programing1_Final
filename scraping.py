
import requests
import sqlite3
import time
from bs4 import BeautifulSoup


# スター数を整数に変換
def convert_stars(text):
    text = text.strip().lower().replace(",", "")

    if text.endswith("k"):
        return int(float(text[:-1]) * 1000)
    elif text.endswith("m"):
        return int(float(text[:-1]) * 1000000)

    return int(text)


url = "https://github.com/orgs/google/repositories"
records = []

# 2ページ分スクレイピング
for page in range(1, 3):
    if page > 1:
        time.sleep(1)

    print(f"{page}ページ目を取得中...", flush=True)

    response = requests.get(
        url, params={"page": page}, timeout=15
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    repos = soup.find_all("h3")

    count = 0

    for repo in repos:
        container = repo.find_parent("li")

        if container is None:
            continue

        name = repo.get_text(" ", strip=True)

        language_tag = container.select_one(
            'span[class^="PrimaryLanguageName"]'
        )
        language = (
            language_tag.get_text(strip=True)
            if language_tag else None
        )

        stars_tag = container.select_one(
            'a[href$="/stargazers"]'
        )
        stars = (
            convert_stars(stars_tag.get_text(" ", strip=True))
            if stars_tag else None
        )

        records.append((name, language, stars))
        count += 1

    print(f"{page}ページ目: {count}件取得完了", flush=True)


# データベースに接続
conn = sqlite3.connect("repositories.db")
cursor = conn.cursor()

# テーブル作成
cursor.execute("""
CREATE TABLE IF NOT EXISTS repositories (
    name TEXT PRIMARY KEY,
    language TEXT,
    stars INTEGER
)
""")

# データを保存
print("保存中...", flush=True)

cursor.executemany("""
INSERT OR REPLACE INTO repositories (name, language, stars)
VALUES (?, ?, ?)
""", records)

conn.commit()
print("保存完了", flush=True)

# SELECTでデータを表示
cursor.execute("SELECT name, language, stars FROM repositories")

for row in cursor.fetchall():
    print(row)

conn.close()
