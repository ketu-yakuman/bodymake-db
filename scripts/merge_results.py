"""
使い方:
    python3 scripts/merge_results.py <生テキストファイル> <competitionId>

やること:
1. parse_pdf_text.py でPDFの生テキストを行データに変換
2. 選手を (氏名, 都道府県) で名寄せし、既存のathletes.jsonにいなければ新規追加
3. results.json に「どの選手がどの大会の何位だったか」を追記
4. 新規追加した選手は confidence: "new" を付け、後で目視確認しやすくする

このスクリプトは「JBBFの日本選手権・マスターズ選手権と同じレイアウト」の
PDFテキストにのみ対応しています。他団体・他形式のPDFではparse_pdf_text.py
側の調整が別途必要です。
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from parse_pdf_text import parse_text

DATA_DIR = Path(__file__).parent.parent / "src" / "data"


def load(name):
    path = DATA_DIR / name
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(name, data):
    path = DATA_DIR / name
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def slugify_id(existing_ids, prefix="a"):
    n = 1
    while f"{prefix}{n:04d}" in existing_ids:
        n += 1
    return f"{prefix}{n:04d}"


def main():
    if len(sys.argv) != 3:
        print("使い方: python3 scripts/merge_results.py <生テキストファイル> <competitionId>")
        sys.exit(1)

    raw_path, competition_id = sys.argv[1], sys.argv[2]
    raw_text = Path(raw_path).read_text(encoding="utf-8")
    rows = parse_text(raw_text)

    athletes = load("athletes.json")
    results = load("results.json")
    competitions = load("competitions.json")

    if not any(c["id"] == competition_id for c in competitions):
        print(f"⚠ competitions.json に競技会ID '{competition_id}' が見つかりません。"
              f"先にcompetitions.jsonへ追加してください。")
        sys.exit(1)

    # 名寄せ用インデックス: (氏名, 都道府県) -> athleteId
    index = {(a["name"], a.get("prefecture")): a["id"] for a in athletes}
    existing_ids = {a["id"] for a in athletes}

    new_athletes = []
    new_results = []
    next_result_no = len(results) + 1

    for row in rows:
        key = (row["name"], row["prefecture"])
        if key in index:
            athlete_id = index[key]
            confidence = "matched"
        else:
            athlete_id = slugify_id(existing_ids)
            existing_ids.add(athlete_id)
            index[key] = athlete_id
            new_athlete = {
                "id": athlete_id,
                "name": row["name"],
                "prefecture": row["prefecture"],
                "club": row["club"],
                "firstSeen": None,
            }
            athletes.append(new_athlete)
            new_athletes.append(new_athlete)
            confidence = "new"

        result = {
            "id": f"r{next_result_no:05d}",
            "athleteId": athlete_id,
            "competitionId": competition_id,
            "category": row["category"],
            "rank": row["rank"],
            "confidence": confidence,
        }
        results.append(result)
        new_results.append(result)
        next_result_no += 1

    save("athletes.json", athletes)
    save("results.json", results)

    print(f"✓ {len(new_results)}件の結果を追加しました(大会: {competition_id})")
    print(f"✓ 新規選手: {len(new_athletes)}名 / 既存選手にマッチ: {len(new_results) - len(new_athletes)}名")
    if new_athletes:
        print("\n--- 新規追加された選手(要目視確認) ---")
        for a in new_athletes[:10]:
            print(f'  {a["id"]}: {a["name"]}（{a["prefecture"]} / {a["club"]}）')
        if len(new_athletes) > 10:
            print(f"  ...ほか{len(new_athletes) - 10}名")


if __name__ == "__main__":
    main()
