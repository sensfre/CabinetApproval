""" 動画 : 支持率 -- 不支持率 最新値(２次元プロット)

"""
import sys
import os
import argparse
import time
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as anm

from fileio import dt_fm_sn, sn_fm_dt
from polldb import t_max
from db_defs import db_defs

cfg = {
    'gout_date': datetime.now().strftime('%Y%m%d'), # 出力file 名に付加する日付
    'avg': False,
    'args': None,    # parse_args() の戻り値を保持する
}

def _d(s):
    return datetime.strptime(s, '%Y-%m-%d')
    
def options():
    """ オプション定義
    Returns
    -------
    opt : ArgumentParser() インスタンス
    
    """
    opt = argparse.ArgumentParser(description='動画 支持率-不支持率 ２次元プロット')
    
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
    # opt.add_argument('-g', '--gout', action='store_true',
    #             help='グラフのファイル出力')
    opt.add_argument('-f', dest='gout_folder', default='../output',
                help='動画の出力先フォルダ (../out)')
    opt.add_argument('-n', dest='gout_ndx', type=int, default=1,
                help='動画の(先頭)図番号 Mov# (1)')
    
    # APP -- NAP グラフ
    opt.add_argument('-r', dest='xy_range', default="20:70",
               help='X軸, Y軸のレンジ (20:70)')
    # opt.add_argument('-t', dest='trimday', default=None,
    #            help='直近 n 日の結果を抽出 (-t14 for last 2 weeks)') 
    
    return opt
    
    
class UPDATE:
    
    def __init__(self, fig):
        
        # DB 読み込み
        #   DB の読み込み日付の指定.
        #   ma_days は感度解析に使うものなので、本アプリでは不用だが省略できないので.
        #
        args = cfg['args']
        d0 = _d(args.db_begin)
        df = _d(args.db_end)
        self.pp2, self.pp3, self.ppj = db_defs(d0, df, args.db_folder, args.ma_days)
        
        # 評価日時 (10 日毎)
        self.t0 = sn_fm_dt(d0)
        self.tf = max(t_max(self.pp2), t_max(self.pp3), t_max(self.ppj)) + 10
        self.tt = [a for a in range(int(self.t0), int(self.tf), 10)] + [int(self.tf)]*10  # 終端に tf を 10 回繰り返し。
        
        # figure & axis 生成
        #
        self.fig = fig
        self.ax = fig.add_subplot(1, 1, 1)
        self.fig.subplots_adjust(left=0)
        
        """
        if cfg['avg']:
            h = 0.67
            self.fig.text(0.19, h + 0.15, "グループ H: 読売/日経/共同/FNN の平均", fontsize=10) #, bbox=bbox)
            self.fig.text(0.19, h + 0.12, "グループ L: 毎日/朝日/時事/ANN/NHK の平均", fontsize=10) #, bbox=bbox)
        """
        
    def set_labels(self):
        self.ax.set_aspect('equal')
        
        xymin, xymax = [int(a) for a in cfg['args'].xy_range.split(':')] # X軸,Y軸の範囲(X,Y 共通)
        self.ax.set_xlim((xymin, xymax))
        self.ax.set_ylim((xymin, xymax))
        
        y1, m1 = [int(a) for a in dt_fm_sn(self.t0).strftime('%Y %m').split()]
        y2, m2 = [int(a) for a in dt_fm_sn(self.tf).strftime('%Y %m').split()]
        self.ax.set_title('内閣支持率(%d年%d月～%d年%d月)' % (y1, m1, y2, m2))
        
        self.ax.set_xlabel('支持する[%]', fontsize=14)
        self.ax.set_ylabel('支持しない[%]', fontsize=14)
        
        self.ax.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0))
        self.ax.grid(True)
        
    def __call__(self, i):
        # 進行状況を画面出力
        sys.stdout.write('%s %s\r' % (i, dt_fm_sn(self.tt[i]).strftime('%Y-%m-%d')))
        
        # クリア
        self.ax.cla()
        
        # 描画
        for (pp, yc, g) in [(self.ppj, 'brown', 'jnn'), (self.pp2, 'indigo', 'グループ H'), (self.pp3, 'green', 'グループ L')]:
            if False and cfg['avg']:
                if g != 'jnn':
                    x_ = np.mean([p.interp['APP_RATE'](self.tt[i]) for p in pp])
                    y_ = np.mean([p.interp['NAP_RATE'](self.tt[i]) for p in pp])
                    self.ax.plot(x_, y_, '*', color=yc, label=g)
            else:
                for p in pp:
                    if True or p.label in ['読売', '毎日', '朝日']:
                        x = p.interp['APP_RATE'](self.tt[i])
                        y = p.interp['NAP_RATE'](self.tt[i])
                        s = '%s %s' % (p.label, dt_fm_sn(p.db['T'][-1]).strftime('%m/%d'))
                        self.ax.plot(x, y, p.marker, ms = p.size, color=yc, label=s, alpha=0.5)
                    else:
                        pass
        x_ = np.mean([p.interp['APP_RATE'](self.tt[i]) for p in self.pp3])
        y_ = np.mean([p.interp['NAP_RATE'](self.tt[i]) for p in self.pp3])
        self.ax.text(x_-8, y_-8, nen_tsuki(dt_fm_sn(self.tt[i])), alpha=0.5, fontsize=16)
        self.ax.plot([0,100], [0,100], '--', color='gray', alpha=0.3)
        
        self.set_labels()
        
def nen_tsuki(dt):
    ys = dt.strftime('%Y')
    ms = dt.strftime('%m')
    return '%s年%s月' % (ys, ms)
    
def main():
    # オプション設定 (cfg['args'] に記録)
    #
    opt = options()
    cfg['args'] = opt.parse_args()
    
    """
    if len(sys.argv) == 2:
        if sys.argv[1] == 'a':
            cfg['avg'] = True
    
    """
    
    args = cfg['args']
    fig = plt.figure()
    update = UPDATE(fig)
    ani = anm.FuncAnimation(fig, update, interval=100, frames=len(update.tt))
    fn = os.path.join(args.gout_folder, 'Mov%d_%s.mp4' % (args.gout_ndx, cfg['gout_date']))
    ani.save(fn, writer='ffmpeg')
    
main()
