"""
JBBF結果PDFのテキスト(web_fetch等で抽出したもの)を、
{rank, no, name, prefecture, club, category} のリストに変換するパーサー。

対応済みの癖:
- 「1位」(半角)・「２位」(全角)どちらの表記にも対応
- カテゴリーラベルは結果の"後"に出てくる(ページ末尾)ことに対応
- カテゴリー名の直後には判定員名(1文字ずつスペース区切り)が続くため、
  そのパターンを検知してカテゴリー名だけを切り出す
- 丸数字(①〜⑤)は「同じカテゴリーの結果が複数ページに分かれているだけ」
  なので、カテゴリー名からは除去して1つのカテゴリーに統合する
- 「欠場」「社会人」は都道府県ではなく特別な値として許容
- 決勝進出できなかった選手(順位表記なし)も finaled=False として抽出
- 都道府県が「東京都」ではなく「東京」のように末尾の都/道/府/県を省略した
  表記(2022年大会で確認)にも対応。「欠 場」のようにスペースが入る表記にも対応

既知の制限:
- 団体・大会タイプが変われば、この正規表現はそのまま使えない可能性が高い。
  新しいPDF書式に当たったら、まずこのファイルの row_re / extract_category
  を実データで検証し直すこと。
"""

import re

_PREF_ABBR = [
    "北海", "青森", "岩手", "宮城", "秋田", "山形", "福島", "茨城", "栃木", "群馬",
    "埼玉", "千葉", "東京", "神奈川", "新潟", "富山", "石川", "福井", "山梨", "長野",
    "岐阜", "静岡", "愛知", "三重", "滋賀", "京都", "大阪", "兵庫", "奈良", "和歌山",
    "鳥取", "島根", "岡山", "広島", "山口", "徳島", "香川", "愛媛", "高知", "福岡",
    "佐賀", "長崎", "熊本", "大分", "宮崎", "鹿児島", "沖縄",
]
_PREF_ABBR_PATTERN = "|".join(r"\s*".join(list(p)) for p in _PREF_ABBR)

# 略記(東京)をこれまでの表記(東京都)に正規化するための逆引き
_PREF_NORMALIZE = {}
for _abbr in _PREF_ABBR:
    if _abbr == "北海":
        _PREF_NORMALIZE[_abbr] = "北海道"
    elif _abbr in ("東京",):
        _PREF_NORMALIZE[_abbr] = _abbr + "都"
    elif _abbr in ("大阪", "京都"):
        _PREF_NORMALIZE[_abbr] = _abbr + "府"
    else:
        _PREF_NORMALIZE[_abbr] = _abbr + "県"


def _normalize_pref(raw):
    cleaned = raw.replace(" ", "").replace("　", "")
    return _PREF_NORMALIZE.get(cleaned, cleaned)


row_re = re.compile(
    r"^(?:(?P<rank>[0-9０-９]+)位\s+)?(?P<no>\d+)\s+(?P<name>[^\d]+?)\s+"
    r"(?P<pref>\S+?(?:県|府|都|道)|" + _PREF_ABBR_PATTERN + r"|欠\s*場|日本社会人|社会人)\s+(?P<rest>.+)$"
)

_ZEN_TO_HAN = str.maketrans("０１２３４５６７８９", "0123456789")


def _to_int(s):
    return int(s.translate(_ZEN_TO_HAN))


def extract_category(line):
    text = line[len("カテゴリー"):].strip()
    tokens = text.split(" ")
    for i in range(len(tokens) - 1):
        if len(tokens[i]) == 1 and len(tokens[i + 1]) == 1:
            return " ".join(tokens[:i]).strip()
    return re.sub(r"\s*[①②③④⑤]\s*$", "", text).strip()


def parse_text(raw_text):
    """PDFから抽出した生テキスト(1本)を渡すと、結果の辞書のリストを返す"""
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

        tokens = m.group("rest").split(" ")
        club_tokens = []
        for t in tokens:
            if t == "*" or re.fullmatch(r"[0-9０-９]+", t):
                break
            club_tokens.append(t)
        club = " ".join(club_tokens).strip()
        name = m.group("name").replace("　", "").replace(" ", "")
        rank = _to_int(m.group("rank")) if m.group("rank") else None

        pending.append({
            "rank": rank,
            "no": _to_int(m.group("no")),
            "name": name,
            "prefecture": _normalize_pref(m.group("pref")),
            "club": club,
            "finaled": rank is not None,
        })

    return results
