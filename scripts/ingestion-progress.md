# JBBF大会 取り込み進捗管理

このファイルは、bodymake-dbに取り込んだ大会・まだ取り込んでいない大会を管理するための
チェックリストです。地方大会まで含めると数百大会規模になるため、複数回のセッションに
分けて進めます。作業のたびにこのファイルを更新し、次回以降どこから再開するかの目印にします。

データソース: http://bodybuilding-fitness.jp/Result/Japan.html (JBBF主催選手権 審査結果一覧表)

## 進め方の方針

1. 全国大会(JBBF主催)を新しい年度から遡って優先的に取り込む
2. 地方大会(都道府県連盟主催)は、各都道府県連盟のサイトを個別に調査してから着手する
   (長崎県のように独自サイトを持つ連盟がある一方、情報がSNS中心の連盟もある可能性が高い)
3. 2015年以前の大会は、PDFがスキャン画像(テキスト抽出不可)である可能性が高いため、
   着手前に個別確認が必要
4. 1大会取り込むごとに、このファイルのチェックボックスを更新する

## フェーズ1: 2025年 全国大会

- [x] jbbf-nihon-2025: 日本男子ボディビル選手権大会・日本女子フィジーク選手権大会 (2025-10-12)
- [x] jbbf-masters-2025: ALL JAPAN MASTERS FITNESS CHAMPIONSHIPS 2025 (2025-09-13)
- [x] jbbf-sportec-2025: Wellni SPORTEC CUP 2025 (2025-08-01)
  http://bodybuilding-fitness.jp/Result/2025/250801_Wellni_SportecCup2025_Result.pdf
  ※メンズフィジーク・マスキュラーメンズフィジーク・ボディフィットネス・
    ウエルネスフィットネス・ビキニフィットネス・クラシックフィジークの6カテゴリー
- [ ] ジャパンオープン選手権大会(第36回) (2025-08-10)
  http://bodybuilding-fitness.jp/Result/2025/250810_JapanOpen_Result.pdf
- [ ] 日本クラシックボディビル選手権大会(第17回) (2025-08-10)
  http://bodybuilding-fitness.jp/Result/2025/250810_NihonClassicBodybuildiong_Reuslt.pdf
- [ ] ALL JAPAN FITNESS CHAMPIONSHIPS 2025 (2025-08-10表記、実体は要確認)
- [ ] 日本ジュニア男子ボディビル選手権大会 他ジュニア/高校の部 (2025-08-24)
  http://bodybuilding-fitness.jp/Result/2025/250824_Nihon_Junior_Bodybuilding_Result.pdf ほか複数
- [ ] 日本マスターズ選手権大会(第37回) (2025-08-31)
  http://bodybuilding-fitness.jp/Result/2025/250831_Nihon_Masters_Result.pdf
- [ ] 日本クラス別選手権大会(第29回) (2025-09-07)
  http://bodybuilding-fitness.jp/Result/2025/250907_Nihon_Class_Result.pdf
- [ ] ALL JAPAN FITNESS CHAMPIONSHIPS 2025 (2025-09-14)
  http://bodybuilding-fitness.jp/Result/2025/250914_AllJapan_Fitness_2025_Result.pdf
- [ ] オールジャパンフィットモデル・ウェルネスチャンピオンシップス2025 (2025-09-21)
  http://bodybuilding-fitness.jp/Result/2025/250921_AllJapan_Fit-Model_Wellness_Result.pdf
- [ ] 日本クラシックフィジーク選手権大会(第5回) (2025-09-21)
  http://bodybuilding-fitness.jp/Result/2025/250921_Nihon_ClassicPhysique_Result.pdf
  ※参考: 同日程で250921_Result.pdfというファイルも存在(内容重複の可能性、要確認)
- [ ] JBBF FITNESS JAPAN GRAND CHAMPIONSHIPS 2025 (2025-10-12)
  http://bodybuilding-fitness.jp/Result/2025/251012_Fitness_Japan_Grand_2025_Result.pdf

## フェーズ2: 2024年 全国大会

- [ ] SPORTEC CUP 2024 (2024-07-18)
- [ ] ジャパンオープン選手権大会(第35回)・日本クラシックボディビル選手権大会(第16回)・
      ALL JAPAN FITNESS CHAMPIONSHIPS 2024 (2024-08-11)
- [ ] 日本ジュニア男子ボディビル選手権大会(第36回) 他 (2024-08-25)
- [ ] オールジャパンフィットモデル/ウェルネス/日本クラシックフィジーク選手権(第3回) (2024-09-01)
- [ ] 日本クラス別選手権大会(第27回) (2024-09-08)
- [ ] 日本マスターズ選手権大会(第36回) (2024-09-15)
- [ ] ALL JAPAN MASTERS FITNESS CHAMPIONSHIPS 2024 (2024-09-28)
- [ ] ALL JAPAN FITNESS CHAMPIONSHIPS 2024 (2024-09-29)
- [x] jbbf-nihon-2024相当: 日本男子ボディビル選手権(第70回)・日本女子フィジーク選手権(第42回) (2024-10-06)
      ※注: これはこれまでのサンプルデータの中に架空データとしてのみ存在。実データ未取り込み
- [ ] JBBF FITNESS JAPAN GRAND CHAMPIONSHIPS 2024 (2024-10-06)
- [ ] 2024 IFBB世界フィットネス選手権・ミズワールドカップ in 東京 (2024-12-17〜19、国際大会・扱い要検討)

## フェーズ3: 2015〜2023年 全国大会

未着手。年ごとにURL一覧はあるが、フォーマットが年によって異なる可能性が高いため、
着手時に都度サンプル確認が必要。

## フェーズ4: 2014年以前

未着手。PDFがスキャン画像(テキスト抽出不可)の可能性が高く、着手前に個別確認が必要。
テキスト抽出できない場合、OCRでの対応可否を別途検討する。

## フェーズ5: 地方大会(都道府県連盟主催)

未着手。47都道府県それぞれの連盟サイトの有無・URL・フォーマットを洗い出すところから開始する。
JBBFの公式サイト(jbbf.jp)に加盟連盟一覧があるはずなので、そこから着手するのが良さそう。
確認済み: 長崎県ボディビル・フィットネス連盟は独自サイトあり(https://www.jbbf-nagasaki.com/result/index.html)

## 既知のパーサー対応状況

- `scripts/parse_pdf_text.py` は「日本選手権型(丸数字でページ分割)」「マスターズ型
  (階級名がそのままラベル)」の2パターンに対応済み
- 新しい大会を取り込む際は、まずそのPDFのカテゴリーラベルの書き方が既知の2パターンに
  当てはまるか確認し、当てはまらなければパーサーの拡張が必要
