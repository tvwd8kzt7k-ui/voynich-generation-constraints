# Timm 公開生成本文の external-model audit

固定された公開生成本文に、このリポジトリの frozen EVA normalization・12-slot decoder・family map を適用する外部モデル監査です。生成器自体の再実行でも、解読でもありません。既存 v0.8 canonical analyses・結果・frozen checkpoints は変更しません。

## 再現

Python 3.10以上、標準ライブラリのみを使用します。初回はネット接続が必要です。リポジトリのルートで実行します。

```bash
python external_validation/timm/run.py --fetch --check external_validation/timm/expected_results.json
```

正常終了時の最終行は `CHECK OK`、終了コードは0です。これは**数値チェックポイントの再現成功**であり、TimmモデルがすべてのVoynich制約に合致するという意味ではありません。Box-0の主結果と互換診断は分離して検証します（後述）。

machine-readable JSON は `external_validation/timm/results.json` に出力します。数値不一致でも計算結果と `verification.errors` を保存し、非0で終了します。欠損入力、誤ったblob、形式異常もエラーJSONを保存して非0で終了します。誤ったキャッシュを黙って再取得・置換しません。

Timm本文・辞書は `external_validation/timm/data/`、ZL3bは既存の `data/ZL3b-n.txt` に保存します。入力と生成結果はGit追跡対象外で、既存解析の出力を上書きしません。取得後は `--fetch` を省略してオフラインで実行できます。`--timm-input`、`--zl3b-input`、`--dictionary-dir`、`--output` でパスを指定できます。ローカル入力も毎回blob検証します。

```bash
python -m unittest discover -s external_validation/timm -p 'test_*.py' -v
python tools/run_all_evidence.py --fetch
```

前者はadapterと異常入力のテスト、後者は既存ZL3b・IT2aの再現テストです。`.github/workflows/external-timm.yml` は既存v0.8 workflowから独立し、数値不一致の場合も結果JSONをartifactに保存します。

## 入力の固定

- Repository: [TorstenTimm/SelfCitationTextgenerator](https://github.com/TorstenTimm/SelfCitationTextgenerator)
- Commit: `a6ede2202dd7ad6285ce2c007bf22c2a0e7709b7`
- File: `executable/generate/generated_text.txt`
- Git blob SHA-1: `31b5f847097d6c31e210d1ebc23ea9878f456607`

辞書も同一コミットの `source/src/main/java/de/voynich/text/canfollow/vms/` 以下を使用します。

| ファイル | Git blob SHA-1 |
| --- | --- |
| VoynichGroups.java | `a06a1a57bd92a6087126109c5f275547b0d47e04` |
| VoynichGroupsTwo.java | `95883bd8472db6b8ef386e81b13e86814ab624df` |
| VoynichGroupsThree.java | `86b8bf5c6ce22964ea1e30a851f37a4a97d84741` |

`VoynichCanFollow.isValid()` は `VoynichGroups.getVoynichDictionary()` の集合への完全一致を判定します。集合は3つの `GROUPS` 配列の第1列の和集合です。監査は3配列を検証・解析して8,026語形の集合を作り、本文の原表記と比較します。辞書判定前にEVA normalizationは行いません。

ZL3bは既存frozen moduleのcommit `729aad62d12483c549e64a2541d4f9255538c8cf`、path `benchmark/unsolved/sources/voynich/transcriptions/ZL3b-n.txt`、blob `2a4533ab9bdfa85db9bad602d590978953055df1` を使用します。生バイト列にGitの `blob <length>\0` 接頭辞を付けてSHA-1を計算します。URLはすべてコミット指定です。本文・辞書ソースは再配布しません。

## 本文と分類

ヘッダーの `text.lines_per_page=29` を確認し、連続29行を1ページとします。本文は1,200行、10,832 whitespace tokensです。page/lineは出力に実在する構造であり、写本固有のbifolio・hand・contextは捏造しません。

ヘッダー不足、途中のコメント、空行、不正文字、行数不一致はエラーです。正常な本文内の12-slot invalid tokenは形式異常とは区別して数を記録します。**Timmの“VMS token”と12-slot valid tokenは別の分類**です。

| 本文の交差分類 | 12-slot valid | 12-slot invalid |
| --- | ---: | ---: |
| Timm辞書に完全一致 | 6,878 | 798 |
| Timm辞書にない | 978 | 2,178 |
| 合計 | 7,856 | 2,976 |

ヘッダーにはVMS=7,678、None VMS=3,156、合計10,834と記載されています。本文では辞書内7,676、辞書外3,156、合計10,832です。**辞書内の2 tokenの差をJSONに記録し、解析には実際の書き出し本文のみを使用します。** 不足分は補いません。

## 計測定義と結果

### 1. Line-preserving null

familyが3 concrete faces以上のoccupied slotイベントを使います。同一slot/familyの直前イベントとの一致率を評価し、履歴はページ境界でリセットします。invalid tokenを除いても行境界は保持し、最後のpartial pageも含めます。

行内nullは `sum(c*(c-1))/(n*(n-1))`、行間nullは2行のface比率の内積です。既存frozen同様、連続する有効イベントの行が異なる場合をcross-lineとします。within excess=**0.025169328868808852**、cross-line excess=**-0.008409530115466378**。Voynichと同じ「行内正／行間負」の符号パターンを再現します。

### 2. Exact-form spectrumと長さ調整

Timmは7,856 valid tokens、913 exact types、354 hapax、count 2–20が492 types、count 21以上が67 typesです。

canonical orderのclean42 ZL3bの24,250 valid tokensから7,856を非復元抽出します。1,000反復、xorshift32のseedは `20260928 + replicate_index`、indexは0–999です。forward partial Fisher–Yatesの `j=i+floor(U*(N-i))` を使います。分位数は `(N-1)*p` による線形補間です。区間は抽出分布の中央95%であり、母集団パラメータの信頼区間ではありません。

| 指標 | Timm | ZL3b中央値 | ZL3b中央95% |
| --- | ---: | ---: | ---: |
| exact types | 913 | 1,515 | 1,472.975–1,556 |
| hapax | 354 | 821 | 775.975–867.025 |
| mid 2–20 | 492 | 618 | 593.975–641 |
| high 21+ | 67 | 76 | 71–82 |

canonical orderの非重複連続7,856-token chunksの `(types,hapax,mid,high)` は、`(1432,744,614,74)`、`(1252,694,477,81)`、`(1480,786,616,78)` です。残り682 tokensは完全なchunkを作らないため除外します。同数のtokensでもTimmのexact-form diversityは低く、特にtypesとhapaxが大幅に少ない結果です。

### 3. Low-dimensional family analog

**Published CAL8 statisticではなく、whole-population, length-matched analog**です。各標本内でcount 21以上のexact formを含むfamilyを選び、そのfamilyの全tokensを評価します。`canonical.tests.low_dimensional_family.modal_stats` と `coverage` を直接再利用します。

slotは `1-modal_share` 降順、同順位はalternative count降順、slot番号昇順です。Box-kは上位k slotsを自由にし、残りをfamilyのmodal faceに固定したtoken比率です。Timmは23 families、5,688 family tokensです。ZL3bは250反復、n=7,856、seed=`2026092800 + replicate_index`（0始まり）です。

| coverage | Timm | ZL3b中央値（canonical同順位規則） |
| --- | ---: | ---: |
| Box-0 | 0.34159634317862164 | 0.4404785856510991 |
| Box-1 | 0.6476793248945147 | 0.6936119546432598 |
| Box-2 | 0.8630450070323488 | 0.8965827071880184 |
| Box-3 | 0.9760900140646976 | 0.9813906633191403 |

Box-3では強い低次元性を再現しますが、Box-0/1/2はVoynichほど集中しません。

### 4. Page-local opposite-half analog

**Bifolio-local testではありません。** 29行の完全な41 pagesのみを使い、最後の11行を除外します。half 0は1–14行、half 1は15–29行。2 faces以上のoccupied slot/family choiceを評価します。

baselineは対象ページを除外した `P(face | slot,family)`、Jeffreys alpha=0.5。反対halfのcountsをbaselineへtauで縮約します。wrong sourceは他40 pagesの同じsource-half indexです。tau gridは5,10,20,50,100,200、focal tau=20を再調整せず使用します。

23,860 events、baseline LL/event=-0.8174740860075324、local=-0.7810010220076306、gain=0.03647306399990185、true−wrong mean=0.06732913091808557です。trueがwrong平均より良い方向は81/82、top1は35/82、top5は71/82、true gainが正のページは38/41、wrong平均との差が正のページは41/41です。

全tau・全方向・各ページをJSONに保存し、負の結果も隠しません。明示的なpage-local source preferenceを検出する**positive control**です。Voynichのbifolio-local effectの直接再現とは解釈しません。

### 5. Uniform exact reuse, page-scope analog

完全な41 pagesの7,780 valid tokensを使います。baselineは対象ページを除外した `P(exact | family)`、alpha=0.5、`canonical.core.support_for_family` による理論的12-slot supportです。

同ページ・同familyで既出のexact formすべてに同じ倍率wを与え、`1+(w-1)*baseline_seen_mass` で正規化します。ページ冒頭で履歴をリセットします。他40 pagesでnested leave-one-page-outを行い、内側の予測対象もbaselineから除外してwを選択します。gridは1,1.1,1.25,1.5,2,3,4,6,8,12、同値なら先の小さいwです。

baseline LL/token=-2.0607177720093595、reuse=-2.027753016289856、gain=0.03296475571950346。37/41 pagesで正、全41 pagesでw=2です。Voynich側はbifolio/context baselineのため、effect magnitudeを直接比較しません。

## Box-0の既知値との差と互換診断

提供された既知値 `0.4404545000047545` は、既存canonicalの同順位処理による `0.4404785856510991` と一致しません。差は約0.00002409です。canonicalは同数のmodal faceをPython文字列順で選び、例えば `E` を `e` より先に選びます。

小文字優先の `(face.lower(), face.isupper())` で選ぶ別診断では提供値を再現します。250反復中20反復のBox-0が変わり、中央値を挟む標本の組み合わせが変わります。この一致だけでは、提供値の元実装がどの規則を使ったかは断定できません。

差を調査・報告し、依頼者の承認を得て分離しました。

- 主結果は既存canonicalの規則を直接利用します。canonicalコードと既存checkpointsは変更しません。
- `box0_modal_tie_sensitivity.lowercase_first_median` に元の指定値を残し、別の互換・感度診断として検証します。
- `expected_results.json` は主結果と互換診断の両方を検証します。
- JSONに変更された20反復のindexと両方の値を保存します。許容誤差を広げて差を隠していません。

## 解釈の上限・適用不能な解析

固定された公開Timm generatorは、行内正／行間負の順序符号、強いpage-local state、page内exact reuse、Box-3での強い低次元性を再現します。長さ調整済みexact-form diversityと、Voynichに見られるBox-0/1/2の強い集中には合致しません。この不一致も `constraint_assessment` に記録します。

写本固有のcontext/hand比較、bifolio-local test、bifolio/context reuse、published CAL8の直接再現は適用不能で、理由を `not_applicable` に記録します。架空のメタデータで代用せず、page-level計測はすべてanalogと明記します。

この結果から、Voynich写本がTimmの機構で作られた、self-citationが証明された、意味内容がない、より広いself-citation／dynamic-production仮説が棄却された、とは結論しません。どのfrozen constraintsを再現し、どれを再現しないかという**固定された公開実装・出力の特徴づけ**に限定します。
