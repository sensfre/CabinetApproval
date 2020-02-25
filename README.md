# 内閣支持率
以下の解析機能を提供します。

* 支持率--不支持率の発表値をそのまま 2 次元グラフにプロットする。
  最新値の画像や動画を作成する。

* 支持率+不支持率が高めのところと低めのところの２グループに分けて、
  内閣支持率の動きを追う。
  グループ内で感度を調整してから平均を求めています。
  感度は、各社の長期移動平均を元に算出しています。

## フォルダー構成

    CabinetApproval -+-- script/   各種解析ツール (作業フォルダ)
                     |
                     +-- data/     報道各社のデータ
                     |
                     +-- output/   出力 (引数で変更可能)

## script
* g_app_nap.py ... 支持率--不支持率 最新値 2D プロット
* g_trend2.py ... ２グループに分けた各種グラフの生成
* edit_header.py ... twitter プロファイル用の画像を編集
* m_app_nap.py ... 動画 (支持率--不支持率 最新値 2D プロット)

## 使い方

    コマンドプロンプトを起動
    cd ./script    (作業フォルダである script に移動)
    g_app_nap.py   コマンドラインでスクリプトを実行

## 依存
numpy/scipy/matplotlib/pillow

## 共通ツール
* fileio.py    np.genfromtxt と 日付連番(Excel の連番に合わせた)
* polldb.py    各社のデータと長期平均を保持するクラス
* db_defs.py   グループ分け & DB の宣言(生成)

![FIG01](https://user-images.githubusercontent.com/52857956/75242926-58bf3800-580c-11ea-9671-a9387011d6d9.png)
