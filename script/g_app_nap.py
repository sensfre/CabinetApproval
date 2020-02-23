""" 支持率 -- 不支持率 最新値(２次元プロット)

"""
import os
import argparse
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

from fileio import dt_fm_sn
from polldb import t_max
from db_defs import db_defs

cfg = {
    'gout_date': datetime.now().strftime('%Y%m%d'), # file 名に日付を付加する
    'args': None,    # parse_args() の戻り値を保持する
}

def proc_last(pp2, pp3, ppj):
    """ 作図 支持率 -- 不支持率 最新値(２次元プロット)
    
    最新値と前回からの差分を 支持率--不支持率 グラフ(２次元)にプロットする。
    オプションで古い最新値を無視する (-t 14 など)。
    オプションでイメージファイル Fig?_yymmdd.png を出力する。
    
    Parameters
    ----------
    pp2, pp3, ppj : グループ毎の DB() リスト.
    
    """
    args = cfg['args']
    xymin, xymax = [int(a) for a in args.xy_range.split(':')] # X軸,Y軸の範囲(X,Y 共通)
    xoff, yoff = [float(a) for a in args.label_offset.split(':')] # ラベルのオフセット
    
    fig = plt.figure(figsize=(4.8*(1800/1012), 4.8))
    fig.subplots_adjust(left=0.02, bottom=0.13, right=0.9, top=0.88)
    ax = fig.add_subplot(1,1,1)
    ax.set_aspect('equal')
    fig.text(0.3, 0.83, '各社の最新(線分は前回からの変化)', fontsize=10,
                bbox=dict(facecolor='gray', edgecolor='none', alpha=0.2))
    ax.set_xlabel('内閣を支持する [%]', fontsize=14)
    ax.set_ylabel('内閣を支持しない [%]', fontsize=14)
    ax.set_xlim(xymin, xymax)
    ax.set_ylim(xymin, xymax)
    ax.set_xticks(range(xymin, xymax + 1, 5))
    ax.set_yticks(range(xymin, xymax + 1, 5))
    ax.grid(True)
    
    # 各社最新
    for (pp, col, ab) in [(ppj, 'brown', 'C'), (pp2, 'indigo', 'グループH'), (pp3, 'green', 'グループL')]:
        for p in pp:
            tref = max(t_max(ppj), t_max(pp2), t_max(pp3))
            # DB の終端からの日にちで絞る(オプショナル)
            if args.trimday and (p.db['T'][-1] < (tref - int(args.trimday))):
                continue
            xx = p.db['APP_RATE'][-2:]
            yy = p.db['NAP_RATE'][-2:]
            st1 = dt_fm_sn(p.db['T'][-1]).strftime('%m/%d')
            st2 = dt_fm_sn(p.db['T'][-2]).strftime('%m/%d')
            s = '%s %s   (%s)' % (p.label, st1, st2)
            ax.plot(xx, yy, '-', lw=1, color=col, alpha=0.4)
            ax.plot(xx[-1], yy[-1], p.marker, ms=p.size, alpha=0.9, label=s)
            # ax.text(xx[-1]+0.2, yy[-1]+0.4, p.label, fontsize=10, alpha=0.8)
            ax.text(xx[-1]+xoff, yy[-1]+yoff, p.label, fontsize=10, alpha=0.8)
            
    ax.plot([0,100], [0,100], '--', alpha=0.5)
    ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1.02))
    if args.gout:
        fn = 'Fig%s_%s.png' % (args.gout_ndx, cfg['gout_date'])
        fig.savefig(os.path.join(args.gout_folder, fn))
    
    
def options():
    """ オプション定義
    Returns
    -------
    opt : ArgumentParser() インスタンス
    
    """
    opt = argparse.ArgumentParser(description='最新の支持率-不支持率 ２次元プロット')
    
    # DB
    opt.add_argument('-d', dest='db_folder', default='../data',
                help='data folder. (../data)')
    opt.add_argument('-b', dest='db_begin', default='2016-04-01',
                help='DB 読み込み開始日付 (2016-04-01)')
    opt.add_argument('-e', dest='db_end', default='2022-12-31',
                help='DB 読み込み終了日付 (2022-12-31)')
    opt.add_argument('-m', dest='ma_days', type=int, default=180,
                help='DB の長期移動平均の窓サイズ [days]. (180)')
    
    # GOUT
    opt.add_argument('-g', '--gout', action='store_true',
                help='グラフのファイル出力')
    opt.add_argument('-f', dest='gout_folder', default='../output',
                help='グラフの出力先フォルダ (../output)')
    opt.add_argument('-n', dest='gout_ndx', type=int, default=10,
                help='グラフの(先頭)図番号 Fig# (10)')
    
    # APP -- NAP グラフ
    opt.add_argument('-r', dest='xy_range', default="30:60",
                help='X軸, Y軸のレンジ (30:60)')
    opt.add_argument('-l', dest='label_offset', default="-2.3:-0.3",
                help='ラベルのオフセット (-2.3:-0.3)')
    opt.add_argument('-t', dest='trimday', default=None,
                help='直近 n 日の結果を抽出 (-t14 for last 2 weeks)') 
    
    return opt
    
    
def _d(s):
    return datetime.strptime(s, '%Y-%m-%d')
    
def main():
    
    # オプション設定 (cfg['args'] に記録)
    #
    opt = options()
    cfg['args'] = opt.parse_args()
    
    # DB 読み込み
    #   DB の読み込み日付の指定.
    #   ma_days は感度解析に使うものなので、本アプリでは不用だが省略できないので.
    #
    args = cfg['args']
    d0 = _d(args.db_begin)
    df = _d(args.db_end)
    pp2, pp3, ppj = db_defs(d0, df, args.db_folder, args.ma_days)
    
    # 作図
    #
    proc_last(pp2, pp3, ppj)
    
    # 表示
    #    イメージファイルの出力は proc_last() 内で行う
    #    複数の図を出力するアプリの plot.show() は一つなので main の最後で実施する
    if args.gout == False:
        plt.show()
    
if __name__ == '__main__':
    main()
    
