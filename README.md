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
  
## 依存
numpy/scipy/matplotlib/pillow

## 共通ツール
* fileio.py    np.genfromtxt と 日付連番(Excel の連番に合わせた)
* polldb.py    各社のデータと長期平均を保持するクラス
* db_defs.py   グループ分け & DB の宣言(生成)

## ツールごとの usage

### g_trend.py
```
usage: g_trend.py [-h] [-d DB_FOLDER] [-b DB_BEGIN] [-e DB_END] [-m MA_DAYS]
                  [-g] [-f GOUT_FOLDER] [-n GOUT_NDX] [-k K_DAYS]

2グループに分けて支持率を追う

optional arguments:
  -h, --help      show this help message and exit
  -d DB_FOLDER    data folder. (../data)
  -b DB_BEGIN     DB 読み込み開始日付 (2016-04-01)
  -e DB_END       DB 読み込み終了日付 (2022-12-31)
  -m MA_DAYS      DB の長期移動平均の窓サイズ [days]. (180)
  -g, --gout      グラフのファイル出力
  -f GOUT_FOLDER  グラフの出力先フォルダ (../output)
  -n GOUT_NDX     グラフの(先頭)図番号 Fig# (1)
  -k K_DAYS       指数移動平均の時定数[day] (10)
```

### g_app_nap.py

```
usage: g_app_nap.py [-h] [-d DB_FOLDER] [-b DB_BEGIN] [-e DB_END] [-m MA_DAYS]
                    [-g] [-f GOUT_FOLDER] [-n GOUT_NDX] [-r XY_RANGE]
                    [-l LABEL_OFFSET] [-t TRIMDAY]

最新の支持率-不支持率 ２次元プロット

optional arguments:
  -h, --help       show this help message and exit
  -d DB_FOLDER     data folder. (../data)
  -b DB_BEGIN      DB 読み込み開始日付 (2016-04-01)
  -e DB_END        DB 読み込み終了日付 (2022-12-31)
  -m MA_DAYS       DB の長期移動平均の窓サイズ [days]. (180)
  -g, --gout       グラフのファイル出力
  -f GOUT_FOLDER   グラフの出力先フォルダ (../output)
  -n GOUT_NDX      グラフの(先頭)図番号 Fig# (10)
  -r XY_RANGE      X軸, Y軸のレンジ (30:60)
  -l LABEL_OFFSET  ラベルのオフセット (-2.3:-0.3)
  -t TRIMDAY       直近 n 日の結果を抽出 (-t14 for last 2 weeks)
```

## 出力例

### g_trend.py
![FIG01](https://user-images.githubusercontent.com/52857956/75243507-57423f80-580d-11ea-9fa1-b3b89f6f3344.png)

### g_app_nap.py
![FIG02](https://user-images.githubusercontent.com/52857956/75244070-670e5380-580e-11ea-8fd3-28a37c5af16d.png)

