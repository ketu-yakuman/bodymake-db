"""
日本選手権型のJBBF結果PDF専用。通常のparse_pdf_text.pyは順位・氏名・所属のみを
抽出するが、こちらは審査結果一覧表そのままの構成(1次ピックアップ・2次ピックアップ・
予選・決勝・合計、審査員ごとのスコア)まで抽出する。

対応済みの列パターン(1行分、氏名・都道府県・所属の後に続くトークン列):
  [*×N + 小計] [*×N + 小計] [得点×N + 小計 + 順位] [得点×N + 小計 + 順位] [合計]
  - ピックアップ(*マーク)は0〜2グループ
  - 得点ラウンド(予選・決勝)は0〜2グループ
  - 全部揃うのは決勝進出者(1〜12位)のみ。それ以外は途中で切れる

現状は審査員7名(A〜G)のケースのみ対応。審査員数が異なるPDFに使う場合は
NUM_JUDGESを都度確認すること。
"""

import re
from parse_pdf_text import row_re, extract_category, _to_int, _normalize_pref


def parse_rounds(tokens, num_judges=7):
    """club抽出後に残ったトークン列から、ピックアップ・得点ラウンドを抽出する"""
    idx = 0
    pickups = []
    while idx < len(tokens) and tokens[idx] == "*":
        start = idx
        while idx < len(tokens) and tokens[idx] == "*":
            idx += 1
        marks = idx - start
        if idx < len(tokens) and re.fullmatch(r"[0-9０-９]+", tokens[idx]):
            pickups.append({"marks": marks, "subtotal": _to_int(tokens[idx])})
            idx += 1
        else:
            break

    remaining = tokens[idx:]
    chunk_size = num_judges + 2
    scored_rounds = []
    i = 0
    while i + chunk_size <= len(remaining) and all(
        re.fullmatch(r"[0-9０-９]+", t) for t in remaining[i:i + chunk_size]
    ):
        chunk = remaining[i:i + chunk_size]
        scored_rounds.append({
            "scores": [_to_int(x) for x in chunk[:num_judges]],
            "subtotal": _to_int(chunk[num_judges]),
            "rank": _to_int(chunk[num_judges + 1]),
        })
        i += chunk_size

    total = None
    if len(scored_rounds) == 2 and i < len(remaining) and re.fullmatch(r"[0-9０-９]+", remaining[i]):
        # 合計は「予選小計+決勝小計」の意味であり、両ラウンドのスコアが揃っている
        # 選手にのみ意味を持つ。片方しか無い場合の末尾の余り数字は、順位や通し番号など
        # 用途が特定できないため、誤解を招く表示を避けて拾わない。
        total = _to_int(remaining[i])

    detail = {
        "judges": ["A", "B", "C", "D", "E", "F", "G"][:num_judges],
        "firstPickup": pickups[0] if len(pickups) >= 1 else None,
        "secondPickup": pickups[1] if len(pickups) >= 2 else None,
        "prelim": scored_rounds[0] if len(scored_rounds) >= 1 else None,
        "final": scored_rounds[1] if len(scored_rounds) >= 2 else None,
        "total": total,
    }
    return detail


def parse_text_with_detail(raw_text, num_judges=7):
    lines = [l.strip() for l in raw_text.splitlines() if l.strip()]

    pending = []
    results = []

    for line in lines:
        if line.startswith("カテゴリー"):
            category = extract_category(line)
            for row in pending:
                row["category"] = category
            results.extend(pending)
            pending = []
            continue

        m = row_re.match(line)
        if not m:
            continue

        rest_tokens = m.group("rest").split(" ")
        club_tokens = []
        j = 0
        while j < len(rest_tokens):
            t = rest_tokens[j]
            if t == "*" or re.fullmatch(r"[0-9０-９]+", t):
                break
            club_tokens.append(t)
            j += 1
        club = " ".join(club_tokens).strip()
        remaining_tokens = [t for t in rest_tokens[j:] if t]

        name = m.group("name").replace("　", "").replace(" ", "")
        rank = _to_int(m.group("rank")) if m.group("rank") else None

        detail = parse_rounds(remaining_tokens, num_judges=num_judges)

        pending.append({
            "rank": rank,
            "no": _to_int(m.group("no")),
            "name": name,
            "prefecture": _normalize_pref(m.group("pref")),
            "club": club,
            "finaled": rank is not None,
            "detail": detail,
        })

    return results
