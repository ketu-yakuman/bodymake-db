"""
2019年以前など、テキスト抽出時に複数選手分のデータが改行なしで連結されてしまう
PDF専用のパーサー。審査員別の詳細スコアは数字自体が連結し復元の信頼性が低いため
取得しない。順位1〜12位(決勝進出者)のみを対象とし、13位以下(予選敗退者)は
No.の連番性が無く安全に分離できないため対象外とする。
"""

import re
from parse_pdf_text import _PREF_ABBR_PATTERN, _normalize_pref, extract_category

_ROW_HEAD_RE = re.compile(
    r"^(?P<no>[0-9０-９]+)\s+(?P<name>[^\d]+?)\s+"
    r"(?P<pref>\S+?(?:県|府|都|道)|" + _PREF_ABBR_PATTERN + r"|欠\s*場|日本社会人|社会人)\s+"
    r"(?P<rest>.+)$"
)

_ZEN_TO_HAN = str.maketrans("０１２３４５６７８９", "0123456789")


def _zenkaku(n):
    return str(n).translate(str.maketrans("0123456789", "０１２３４５６７８９"))


def parse_ranked_only_from_full_text(raw_text, max_rank=12):
    """カテゴリー行を区切りに使い、各カテゴリーの本文(カテゴリー行より前)から
    1位〜max_rank位を抽出する"""
    parts = raw_text.split("カテゴリー")

    results = []
    body = parts[0]
    for i in range(1, len(parts)):
        head = parts[i]
        delim = re.search(r"[①②③④⑤]|\n|開\s*催\s*日", head)
        category = (head[:delim.start()] if delim else head).strip()
        cut = delim.end() if delim else len(head)

        if category and body.strip():
            # 1位から順番に、マーカーの(開始位置, 終了位置)を集める
            markers = []
            pos = 0
            for n in range(1, max_rank + 1):
                pat = re.compile(f"(?:{n}位|{_zenkaku(n)}位)")
                mm = pat.search(body, pos)
                if not mm:
                    break
                markers.append((n, mm.start(), mm.end()))
                pos = mm.end()

            for j, (rank, mstart, mend) in enumerate(markers):
                end = markers[j + 1][1] if j + 1 < len(markers) else len(body)
                chunk = body[mend:end].strip()
                chunk = re.sub(r"\s+", " ", chunk)
                hm = _ROW_HEAD_RE.match(chunk)
                if not hm:
                    continue
                name = hm.group("name").replace("　", "").replace(" ", "")
                pref = _normalize_pref(hm.group("pref"))
                rest_tokens = hm.group("rest").split(" ")
                club_tokens = []
                for t in rest_tokens:
                    if re.fullmatch(r"[\*0-9０-９]+", t):
                        break
                    club_tokens.append(t)
                club = " ".join(club_tokens).strip()
                results.append({
                    "rank": rank,
                    "no": int(str(hm.group("no")).translate(_ZEN_TO_HAN)),
                    "name": name,
                    "prefecture": pref,
                    "club": club,
                    "category": category,
                    "finaled": True,
                })

        body = head[cut:]

    return results
