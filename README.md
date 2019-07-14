# 内閣支持率

支持率+不支持率が高めのところと低めのところの２グループに分けて、
内閣支持率の動きを追います。

## フォルダー構成

    CabinetApproval -+-- script/   各種解析ツール
                     |
                     +-- data/     報道各社のデータ
                     |
                     +-- output/   出力 (引数で変更可能)

## script
* pdat.py ... ２グループに分けた各種グラフの生成
* edit_header.py ... twitter プロファイル用の画像を編集

## 使い方

    コマンドプロンプトを起動
    cd ./script    (作業フォルダである script に移動)
    pdat.py        コマンドラインでスクリプトを実行

## 依存
numpy/matplotlib/pillow
