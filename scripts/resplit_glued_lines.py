"""
古い年度のJBBF結果PDF(Excelの罫線表をそのままPDF化したもの)は、テキスト抽出時に
複数選手分のデータが改行なしで連結されてしまうことがある(例:「...2 10 2 203位 3 加藤...」
のように、ある選手の合計点の直後に次の選手の「3位」が隙間なくくっつく)。

順位(1位〜12位)は必ず連番で並んでいるという既知の構造を手がかりに、
1行に複数選手分が連結されている場合はここで分割し直す。
選手個別の詳細スコア(審査員別の点数)は、数字自体が隙間なく連結してしまい
機械的な復元が信頼できないため、この関数を使うファイルでは詳細スコアの取得は
諦め、順位・氏名・都道府県・所属クラブのみを対象とする。
"""

import re
from parse_pdf_text import _PREF_ABBR_PATTERN

# 行の先頭になり得るパターン: (任意で)"N位" + No + 氏名 + 都道府県
_ROW_START_RE = re.compile(
    r"(?:[0-9０-９]{1,2}位\s*)?[0-9０-９]{1,3}\s+[^\d]{2,24}?\s+"
    r"(?:\S+?(?:県|府|都|道)|" + _PREF_ABBR_PATTERN + r"|欠\s*場|日本社会人|社会人)\s+"
)


def resplit_glued_lines(raw_text):
    """1行に複数選手分のデータが連結されている場合、行を分割し直す。
    カテゴリーの見出し行など、選手データでない行はそのまま素通りする。"""
    fixed_lines = []
    for line in raw_text.splitlines():
        line = line.strip()
        if not line:
            continue
        matches = list(_ROW_START_RE.finditer(line))
        if len(matches) <= 1:
            fixed_lines.append(line)
            continue
        # 2件以上の行データが1行に連結されている場合、開始位置で分割する
        starts = [m.start() for m in matches] + [len(line)]
        for i in range(len(matches)):
            chunk = line[starts[i]:starts[i + 1]].strip()
            if chunk:
                fixed_lines.append(chunk)
    return fixed_lines
