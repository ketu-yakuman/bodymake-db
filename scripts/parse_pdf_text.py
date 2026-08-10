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

既知の制限:
- 団体・大会タイプが変われば、この正規表現はそのまま使えない可能性が高い。
  新しいPDF書式に当たったら、まずこのファイルの row_re / extract_category
  を実データで検証し直すこと。
"""

import re

row_re = re.compile(
    r"^(?:(?P<rank>[0-9０-９]+)位\s+)?(?P<no>\d+)\s+(?P<name>[^\d]+?)\s+"
    r"(?P<pref>\S+?(?:県|府|都|道)|欠場|社会人)\s+(?P<rest>.+)$"
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
            "prefecture": m.group("pref"),
            "club": club,
            "finaled": rank is not None,
        })

    return results
