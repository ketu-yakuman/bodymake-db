"""
JBBFの「出場選手名簿」PDF(審査結果一覧表とは別に、大会前に公表されるエントリーリスト)
を解析する。審査結果一覧表よりずっとシンプルな構成:
    No 選手名 フリガナ 都道府県 年令 身長 所属クラブ

年齢と大会の開催年から生まれ年を逆算できるため、同姓同名の選手を判別する
材料として使う(誕生日が分からないため±1年の誤差がある)。
"""

import re
from parse_pdf_text import _PREF_ABBR_PATTERN, _normalize_pref

list_row_re = re.compile(
    r"^(?P<no>\d+)\s+(?P<name>[^\d]+?)\s+"
    r"(?P<furigana>[ｦ-ﾟA-Za-z\s]+?)\s+"
    r"(?P<pref>\S+?(?:県|府|都|道)|" + _PREF_ABBR_PATTERN + r"|欠\s*場|日本社会人|社会人)\s+"
    r"(?P<age>\d+)[歳才]\s+(?P<height>[\d.]+cm)\s+(?P<club>.+)$"
)


def parse_list_text(raw_text, competition_year):
    """出場選手名簿PDFのテキストから {name, prefecture, age, birthYearEstimate} を抽出"""
    rows = []
    for line in raw_text.splitlines():
        line = line.strip()
        m = list_row_re.match(line)
        if not m:
            continue
        name = m.group("name").replace("　", "").replace(" ", "")
        age = int(m.group("age"))
        rows.append({
            "name": name,
            "prefecture": _normalize_pref(m.group("pref")),
            "age": age,
            "birthYearEstimate": competition_year - age,
        })
    return rows
