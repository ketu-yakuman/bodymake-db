"""
使い方:
    python3 scripts/merge_results.py <生テキストファイル> <competitionId>

やること:
1. parse_pdf_text.py でPDFの生テキストを行データに変換
2. 選手を「氏名のみ」で名寄せする(都道府県の変化=別人とはみなさない。
   引っ越し等で都道府県が変わっても同一選手として追跡できるようにするため)
3. ただし氏名だけでは同姓同名の別人を誤って統合してしまうリスクがあるため、
   マッチ時に都道府県が過去の記録と食い違う場合は警告を出し、
   scripts/name-collision-warnings.md に記録する(要目視確認)
4. athlete-splits.json に登録済みの氏名は、都道府県も合わせて判定することで
   強制的に別人として分離できる(同姓同名と判明した場合の手動対処用)
5. results.json に「どの選手がどの大会の何位だったか」を追記
6. 新規追加した選手は confidence: "new" を付け、後で目視確認しやすくする

このスクリプトは「JBBFの日本選手権・マスターズ選手権と同じレイアウト」の
PDFテキストにのみ対応しています。他団体・他形式のPDFではparse_pdf_text.py
側の調整が別途必要です。
"""

import sys
import json
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from parse_pdf_text import parse_text

DATA_DIR = Path(__file__).parent.parent / "src" / "data"
SCRIPTS_DIR = Path(__file__).parent
SPLITS_PATH = SCRIPTS_DIR / "athlete-splits.json"
WARNINGS_PATH = SCRIPTS_DIR / "name-collision-warnings.md"

_PLACEHOLDER_PREFS = {"欠場", "社会人", "日本社会人"}


def _is_genuine_pref_change(old, new):
    """欠場/社会人のようなプレースホルダー値との入れ替わりは、
    実際の都道府県変化(=同姓同名の疑い)としてはノイズなので除外する"""
    if old == new:
        return False
    if old in _PLACEHOLDER_PREFS or new in _PLACEHOLDER_PREFS:
        return False
    return True


def load(name):
    path = DATA_DIR / name
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(name, data):
    path = DATA_DIR / name
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def load_splits():
    """同姓同名の別人と判明し、氏名のみでの名寄せから除外したい選手名の一覧。
    ["田中太郎", ...] のようなJSON配列。ファイルが無ければ空リスト扱い。"""
    if SPLITS_PATH.exists():
        with open(SPLITS_PATH, encoding="utf-8") as f:
            return set(json.load(f))
    return set()


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
    splits = load_splits()

    if not any(c["id"] == competition_id for c in competitions):
        print(f"⚠ competitions.json に競技会ID '{competition_id}' が見つかりません。"
              f"先にcompetitions.jsonへ追加してください。")
        sys.exit(1)

    # 通常は氏名のみで名寄せする。athlete-splits.jsonに載っている氏名だけは
    # (氏名, 都道府県)で判定し、強制的に別人として分離する。
    name_index = {}       # name -> athleteId (splits対象外の選手)
    split_index = {}      # (name, prefecture) -> athleteId (splits対象の選手)
    for a in athletes:
        if a["name"] in splits:
            split_index[(a["name"], a.get("prefecture"))] = a["id"]
        else:
            name_index[a["name"]] = a["id"]
    existing_ids = {a["id"] for a in athletes}
    athletes_by_id = {a["id"]: a for a in athletes}

    new_athletes = []
    new_results = []
    collision_warnings = []
    next_result_no = len(results) + 1

    for row in rows:
        name, pref = row["name"], row["prefecture"]
        confidence = "matched"

        if name in splits:
            key = (name, pref)
            if key in split_index:
                athlete_id = split_index[key]
            else:
                athlete_id = slugify_id(existing_ids)
                existing_ids.add(athlete_id)
                split_index[key] = athlete_id
                new_athlete = {"id": athlete_id, "name": name, "prefecture": pref,
                               "club": row["club"], "firstSeen": None}
                athletes.append(new_athlete)
                athletes_by_id[athlete_id] = new_athlete
                new_athletes.append(new_athlete)
                confidence = "new"
        else:
            if name in name_index:
                athlete_id = name_index[name]
                existing = athletes_by_id[athlete_id]
                old_pref = existing.get("prefecture")
                if old_pref and _is_genuine_pref_change(old_pref, pref):
                    confidence = "matched_prefecture_changed"
                    collision_warnings.append({
                        "name": name, "athleteId": athlete_id,
                        "previousPrefecture": old_pref,
                        "newPrefecture": pref, "competitionId": competition_id,
                    })
                # プレースホルダー(欠場/社会人)より実際の都道府県を優先して保持する
                if pref not in _PLACEHOLDER_PREFS or not old_pref:
                    existing["prefecture"] = pref
                    existing["club"] = row["club"]
            else:
                athlete_id = slugify_id(existing_ids)
                existing_ids.add(athlete_id)
                name_index[name] = athlete_id
                new_athlete = {"id": athlete_id, "name": name, "prefecture": pref,
                               "club": row["club"], "firstSeen": None}
                athletes.append(new_athlete)
                athletes_by_id[athlete_id] = new_athlete
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

    if collision_warnings:
        with open(WARNINGS_PATH, "a", encoding="utf-8") as f:
            f.write(f"\n## {competition_id} 取り込み時 ({datetime.now().strftime('%Y-%m-%d %H:%M')})\n\n")
            for w in collision_warnings:
                f.write(
                    f"- **{w['name']}**（{w['athleteId']}）: "
                    f"{w['previousPrefecture']} → {w['newPrefecture']} に変化 "
                    f"(大会: {w['competitionId']})。同姓同名の別人の可能性があります。要確認。\n"
                )

    print(f"✓ {len(new_results)}件の結果を追加しました(大会: {competition_id})")
    print(f"✓ 新規選手: {len(new_athletes)}名 / 既存選手にマッチ: {len(new_results) - len(new_athletes)}名")
    if collision_warnings:
        print(f"\n⚠ 都道府県の変化を検出({len(collision_warnings)}件) — 同姓同名の可能性、要確認")
        for w in collision_warnings:
            print(f'  {w["athleteId"]}: {w["name"]}（{w["previousPrefecture"]} → {w["newPrefecture"]}）')
        print(f"  詳細は {WARNINGS_PATH.name} に記録しました")
    if new_athletes:
        print("\n--- 新規追加された選手(要目視確認) ---")
        for a in new_athletes[:10]:
            print(f'  {a["id"]}: {a["name"]}（{a["prefecture"]} / {a["club"]}）')
        if len(new_athletes) > 10:
            print(f"  ...ほか{len(new_athletes) - 10}名")


if __name__ == "__main__":
    main()

