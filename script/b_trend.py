"""  支持率 -- 不支持率  (報道 10社の平均)

日曜毎に支持率・不支持率(報道10社平均)を求める

"""
import os
import argparse
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from fileio import dt_fm_sn, sn_fm_dt
from polldb import DB, interp, t_min, t_max, calc_fact
from db_defs import db_defs

cfg = {
    'gout_date': datetime.now().strftime('%Y%m%d'), # file 名に日付を付加する
    'args': None,    # parse_args() の戻り値を保持する
}

def deviation(tt, yy, yi):
    yc = np.array([yi(t) for t in tt])
    yd = yy - yc
    sd = np.std(yd, ddof=1)
    return yd, sd
    
class TVEN:
    """ time, value, error, num
    
    Bugs
    ----
    num > 0 で有効としている。
    error に標準偏差を採用している場合、num == 1 の時に nan 以外を要求する。
    
    """
    def __init__(self, tim, val, err, num):
        self.raw = zip(tim, val, err, num)
        self.buf = self.select_valid(self.raw)

    def select_valid(self, raw):
        return [a for a in raw if a[3] > 0] # 
        
    def by_column(self):
        return [np.array(a) for a in zip(*self.buf)]
        
        
tven_buf = {}

def proc_raw_cal_sdv(fc_dict, axes, column, k_app_nap, pp):
    
    tim, val, err, num = tven_buf[k_app_nap].by_column()
    
    ax =axes[0, column]
    ax.set_ylim(20, 70)
    ax.set_ylabel('調査結果(発表値) %')
    for p in pp:
        dd = [dt_fm_sn(a) for a in p.db['T']]
        ax.plot(dd, p.db[k_app_nap], p.marker, ms=p.size*0.5, label=p.label, alpha=0.5)
    set_date_tick(ax, (1,4,7,10), '%m', 0)
    ax.grid(True)
    ax.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0))
    
    ax =axes[1, column]
    ax.set_ylim(20, 70)
    ax.set_ylabel('感度補正後(曲線は平均値) %')
    ax.set_ylabel('感度補正後 %')
    for p in pp:
        dd = [dt_fm_sn(a) for a in p.db['T']]
        vv = [a/fc_dict[k_app_nap][p.label](b) for a, b in zip(p.db[k_app_nap], p.db['T'])]
        ax.plot(dd, vv, p.marker, ms=p.size*0.5, label=p.label, alpha=0.5)
    dd = [dt_fm_sn(a) for a in tim]
    ee = err/np.sqrt(num)
    ax.fill_between(dd, val-ee, val+ee, color='blue', alpha=0.1)
    ax.plot(dd, val,'-', color='blue', lw=1, alpha=1)
    set_date_tick(ax, (1,4,7,10), '%m', 0)
    ax.grid(True)
    
    ax =axes[2, column]
    ax.set_ylim(-8, 8)
    ax.set_ylabel('感度補正後の残差 %')
    
    for p in pp:
        vv = [a/fc_dict[k_app_nap][p.label](b) for a, b in zip(p.db[k_app_nap], p.db['T'])]
        dv, sd = deviation(p.db['T'], vv, interp(tim, val))
        dd = [dt_fm_sn(a) for a in p.db['T']]
        ax.plot(dd, dv, '-', label=p.label, alpha=0.5)
        
    set_date_tick(ax, (1, 7), '%Y/%m', 30)
    ax.grid(True)
    ax.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0))
    
def proc_summary():
    args = cfg['args']
    
    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax2 = ax1.twinx()
    fig.subplots_adjust(left=0.16, right=0.8, bottom=0.15)
    
    # 色指定
    cy = 'darkorange'
    cy2 = 'orangered'
    cn = 'skyblue'
    cn2 = 'darkcyan'
    
    # ---< 支持率 >---
    tta, ppa_buf, sdv_buf, num_buf = tven_buf['APP_RATE'].by_column()
    dda = [dt_fm_sn(a) for a in tta]
    ax = ax1
    err = sdv_buf/np.sqrt(num_buf)
    ax.fill_between(dda, ppa_buf-err, ppa_buf+err, color=cy, linestyle='dashed', alpha=0.3)
    ax.plot(dda, ppa_buf, color=cy, label='報道10社平均', alpha=1)
    
    # Y 軸
    ax.set_ylim([0, 100])
    ax.tick_params(axis='y', colors=cy2)
    ax.set_yticks(range(0, 51, 10))
    ax.text(datetime(2016, 9, 1), 30, '支持する', color=cy2, fontsize=20)
    ax.set_ylabel('内閣を支持する [%]', color=cy2, fontsize=14)
    ax.yaxis.set_label_coords(-0.08, 0.3)
    
    # ---< 不支持率 >---
    tta, ppa_buf, sdv_buf, num_buf = tven_buf['NAP_RATE'].by_column()
    dda = [dt_fm_sn(a) for a in tta]
    ax = ax2
    err = sdv_buf/np.sqrt(num_buf)
    ax.fill_between(dda, ppa_buf-err, ppa_buf+err, color=cn, linestyle='dashed', alpha=0.3)
    ax.plot(dda, ppa_buf, color=cn, label='報道10社平均', alpha=1)
    
    # Y2 軸
    ax.set_ylim([100, 0])
    ax.tick_params(axis='y', colors=cn2)
    ax.set_yticks(range(0, 51, 10))
    ax.text(datetime(2016, 8, 1), 20, '支持しない', color=cn2, fontsize=20)
    ax.set_ylabel('内閣を支持しない [%]', color=cn2, fontsize=14)
    ax.yaxis.set_label_coords(1.08, 0.7)
    
    # X 軸
    ax = ax1
    ax.xaxis_date()
    ax.set_xlim(dt_fm_sn(tta[0]), dt_fm_sn(30 + tta[-1]))
    set_date_tick(ax, (1, 7), '%Y/%m', 30)
    
    # タイトル/グリッド
    ax1.set_title('報道 10社の平均')
    ax1.grid(which='both')
    ax2.grid(which='both')
    ax1.grid(which='minor', alpha=0.1)
    ax2.grid(which='minor', alpha=0.1)
    
    # 注釈
    # bbox=dict(facecolor='white', edgecolor='none', alpha=0.7)
    if args.k_days > 0:
        fig.text(0.19, 0.16, "平均は指数移動平均(時定数 %d 日)"%args.k_days, fontsize=8) #, bbox=bbox)
    else:
        fig.text(0.19, 0.16, "平均は日曜前後数日", fontsize=8) #, bbox=bbox)
        
    if args.gout:
        fig.savefig(os.path.join(args.gout_folder, 'Fig%d_%s.png' % (args.gout_ndx + 0, cfg['gout_date'])))
    
    
def proc_summary_x(db_list, fc_dict):
    args = cfg['args']
    
    fig, ax = plt.subplots(figsize=(8, 5))
    fig.subplots_adjust(left=0.16, right=0.8, bottom=0.15)
    
    # 色指定
    cy = 'darkorange'
    cn = 'skyblue'
    
    # 支持率
    tim, avg, sdv, num = tven_buf['APP_RATE'].by_column()
    dda = [dt_fm_sn(a) for a in tim]
    err = sdv/np.sqrt(num)
    ax.fill_between(dda, avg-err, avg+err, color=cy, alpha=0.3)
    ax.plot(dda, avg, color=cy, label='支持(平均)', alpha=1)
    
    # 不支持率
    tim, avg, sdv, num = tven_buf['NAP_RATE'].by_column()
    dda = [dt_fm_sn(a) for a in tim]
    err = sdv/np.sqrt(num)
    ax.fill_between(dda, avg-err, avg+err, color=cn, alpha=0.3)
    ax.plot(dda, avg, color=cn, label='不支持(平均)', alpha=1)
    
    # 支持率の個別データ (感度補正後)
    for db in db_list:
        yy = [a/fc_dict['APP_RATE'][db.label](b) for a,b in zip(db.db['APP_RATE'], db.db['T'])]
        dd = [dt_fm_sn(a) for a in db.db['T']]
        ax.plot(dd, yy, db.marker, ms=db.size*0.5, color='orange', alpha=1, label=db.label)
    
    # X 軸
    ax.xaxis_date()
    ax.set_xlim(dt_fm_sn(tim[0]), dt_fm_sn(30 + tim[-1]))
    ax.set_xlim(datetime(2019,2,1), datetime(2020,4,1))  # 日付埋め込み  ★
    set_date_tick(ax, (1, 7), '%Y/%m', 30)
    
    # Y 軸
    ax.set_yticks(range(0, 100, 5))
    ax.set_yticks(range(0, 100, 1), minor=True)
    ax.set_ylim([25, 60])
    
    # タイトル/グリッド
    ax.set_title('報道 10社の平均')
    ax.grid(which='both')
    ax.grid(which='minor', alpha=0.1)
    
    # 凡例
    ax.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0))
    
    # 注釈
    if args.k_days > 0:
        fig.text(0.19, 0.16, "平均は指数移動平均(時定数 %d 日)"%args.k_days, fontsize=8) #, bbox=bbox)
    else:
        fig.text(0.19, 0.16, "平均は日曜前後数日", fontsize=8) #, bbox=bbox)
        
    # 図の出力
    if args.gout:
        fig.savefig(os.path.join(args.gout_folder, 'Fig%d_%s.png' % (args.gout_ndx + 1, cfg['gout_date'])))
    
def set_date_tick(ax, bymonth, format, rotate):
    """ 日付軸の設定
    
    ax : axis
    bymonth : 表示する月のリスト。 ex : [1, 4, 7, 10]
    format : 表示形式。 ex : '%Y/%m'
    rotate : [deg] 文字の回転角。
    
    """
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=bymonth))
    ax.xaxis.set_minor_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter(format))
    
    # 'ax.xaxis.set_tick_params(rotation=45)' does not work ?
    if rotate != 0:
        for label in ax.get_xmajorticklabels():
            label.set_rotation(rotate)
            label.set_horizontalalignment("right")
    
def calc_mav(fc_dict, yn, t_node, db_list, w_days, k_days):
    """
    w_days : [day]  +/-w_days のデータを使う
    k_days : [day] 指数移動平均の時定数
    """
    _tt = []
    _vv = []
    for db in db_list:
        _tt = _tt + list(db.db['T'])
        ff = [fc_dict[yn][db.label](t) for t in db.db['T']]
        vv = [a/b for a, b in zip(db.db[yn], ff)]
        _vv = _vv + list(vv)
    _tt = np.array(_tt)
    _vv = np.array(_vv)
    tt_min = min(_tt)
    
    def _mav(t):
        # 時刻 t における窓付き指数移動平均
        #     w_days : [day] 窓幅
        #     k_days : [day] 時定数
        #
        w_post = max(0, tt_min + w_days - t)
        if 1:
            w_post = w_days
        ndx = (_tt >= t - w_days) & (_tt <= t + w_post)
        tt = _tt[ndx]
        vv = _vv[ndx]
        num = len(tt)
        if num >= 2:
            ww = np.exp(-np.abs(tt - t)/k_days)
            avg = np.sum(ww*vv)/np.sum(ww)
        else:
            avg = np.NaN
        return avg, num
        
    # 全社平均(指数移動平均)を求める。
    #  f_mav(t) は補間関数
    # t_node = [a for a in sorted(np.arange(t_max(db_list), t_min(db_list), -2))]
    v_node, n_node = zip(*[_mav(a) for a in t_node])
    v_node = np.array(v_node)
    
    f_mav = interp(t_node, v_node)
    
    def _err(t):
        w_post = max(0, tt_min + w_days - t)
        if 1:
            w_post = w_days
        ndx = (_tt >= t - w_days) & (_tt <= t + w_post)
        tt = _tt[ndx]
        vv = _vv[ndx]
        d = [v - f_mav(t) for t, v in zip(tt, vv)]
        return np.std(d, ddof=1)
    e_node = [_err(a) for a in t_node]
    
    return TVEN(t_node, v_node, e_node, n_node)
    
    
def calc_every_sunday(fc_dict, yn, t_node, db_list):
    """
    """
    _tt = []
    _vv = []
    for db in db_list:
        _tt = _tt + list(db.db['T'])
        ff = [fc_dict[yn][db.label](t) for t in db.db['T']]
        vv = [a/b for a, b in zip(db.db[yn], ff)]
        _vv = _vv + list(vv)
        
    tv = [(a,b) for (a,b) in zip(_tt, _vv) if not np.isnan(b)]
    _tt, _vv = zip(*tv)
    _tt = np.array(_tt)
    _vv = np.array(_vv)
    
    def _avg(t):
        # t +/-2 day の観測値の平均を求める
        ndx = (_tt >= t - 3) & (_tt <= t + 3)
        tt = _tt[ndx]
        vv = _vv[ndx]
        n = len(vv)
        if n == 0:
            v = np.NaN
            e = np.NaN
        elif n == 1:
            v = np.mean(vv)
            e = 3.5/2 # [pt]  1σ 相当
        else:
            v = np.mean(vv)
            e = max(np.std(vv, ddof=1), 3.5/2)/np.sqrt(n)
        return v, e, n
        
    v_node, e_node, n_node = zip(*[_avg(t) for t in t_node])
    v_node = np.array(v_node)
    e_node = np.array(e_node)
    n_node = np.array(n_node)
    
    return TVEN(t_node, v_node, e_node, n_node)
    
def proc_factor_mav(db_list, k_app_nap, k_title, fc_dict, gn_rel):
    """
    Parameters
    ----------
    db_list, list of DB()
    k_app_nap, string : 分析データキー ('APP_RATE' or 'NAP_RATE')
    k_title, string : グラフタイトル
    
    """
    args = cfg['args']
    
    # 図の準備
    fig, axes = plt.subplots(5, 2, figsize=(10, 7))
    fig.text(0.10, 0.97, k_title, fontsize=16)
    fig.text(0.60, 0.97, '(オレンジ:3ヵ月移動平均  ブルー:6ヵ月移動平均)', fontsize=12)
    fig.subplots_adjust(left=0.1, bottom=0.1, right=0.95, top=0.95, wspace=0.25, hspace=0.25)
    
    # 分析期間
    t0 = sn_fm_dt(_d(cfg['args'].db_begin))
    tf = t_max(db_list)
    
    # 窓幅をいくつか選んで感度のトレンドを描画(調査会社毎)
    for ndx, m in enumerate([3, 6]):  # window size (m-month)
        tt = np.arange(t0 + 6*30, tf, 7)
        ff = calc_fact(db_list, k_app_nap, tt, m*30)
        dd = [dt_fm_sn(a) for a in tt]
        for j, (f, db) in enumerate(zip(ff, db_list)):
            c, r = divmod(j, 5)
            if ndx == 0:
                axes[r,c].plot(dd, f, color='orange', lw=2, alpha=0.8)
            else:
                axes[r,c].plot(dd, f, color='blue')
            fc = [fc_dict[k_app_nap][db.label](t) for t in tt]
            axes[r,c].plot(dd, fc, '-', color='green', alpha=0.5)

    # タイトルや軸の設定
    for j, db in enumerate(db_list):
        c, r = divmod(j, 5)
        axes[r, c].set_ylabel(db.label)
        axes[r, c].set_ylim(0.8, 1.3)
        axes[r, c].grid(which='both')
        axes[r, c].grid(which='minor', alpha=0.1)
        if r <= 3:
            set_date_tick(axes[r,c], (1, 7), '%m', 0)
        else:
            set_date_tick(axes[r,c], (1, 7), '%Y/%m', 30)
        
        # 調査が実施された日付をプロット
        dd_org = [dt_fm_sn(a) for a in db.db['T']]
        oo_org = np.ones_like(dd_org)
        axes[r,c].plot(dd_org, oo_org, 'o', ms=4, alpha=0.2)
    
    if args.gout:
        fig.savefig(os.path.join(args.gout_folder, 'Fig%d_%s.png' % (args.gout_ndx + gn_rel, cfg['gout_date'])))
    
    
def options():
    """ オプション定義
    Returns
    -------
    opt : ArgumentParser() インスタンス
    
    """
    opt = argparse.ArgumentParser(description='2グループに分けて支持率を追う')
    
    # DB
    opt.add_argument('-d', dest='db_folder', default='../data',
                help='data folder. (../data)')
    opt.add_argument('-b', dest='db_begin', default='2016-04-01',
                help='DB 読み込み開始日付 (2016-04-01)')
    opt.add_argument('-e', dest='db_end', default='2022-12-31',
                help='DB 読み込み終了日付 (2022-12-31)')
    opt.add_argument('-m', dest='ma_days', type=int, default=180,
                help='DB の長期移動平均の窓サイズ [days]. (180)') # MA() 不使用なら削除
    
    # GOUT
    opt.add_argument('-g', '--gout', action='store_true',
                help='グラフのファイル出力')
    opt.add_argument('-f', dest='gout_folder', default='../output',
                help='グラフの出力先フォルダ (../output)')
    opt.add_argument('-n', dest='gout_ndx', type=int, default=81,
                help='グラフの(先頭)図番号 Fig# (81)')
    
    # トレンド グラフ
    opt.add_argument('-k', dest='k_days', type=int, default=10,
                help='指数移動平均の時定数[day]  (10)')
    
    return opt
    
def _d(s):
    return datetime.strptime(s, '%Y-%m-%d')
    
def main():
    
    # オプション設定 (cfg['args'] に記録)
    #
    opt = options()
    cfg['args'] = opt.parse_args()
    args = cfg['args']
    
    # DB 読み込み
    #   DB の読み込み日付の指定.
    #   ma_days [day] 感度解析のウィンドウ(直近 ma_days のデータから感度求める)
    #
    args = cfg['args']
    d0 = _d(args.db_begin)
    df = _d(args.db_end)
    pp2, pp3, ppj = db_defs(d0, df, args.db_folder)
    ppa = ppj + pp2 + pp3
    
    # ファクター設定
    fc_dict = {}
    for yn in ['APP_RATE', 'NAP_RATE']:
        fc_dict[yn] = {}
        tstp = 10
        tt = np.arange(t_min(ppa), t_max(ppa), tstp)
        ff_step = calc_fact(ppa, yn, tt, d_window=6*30)
        for p, f in zip(ppa, ff_step):
            fc_dict[yn][p.label] = interp(tt, f)
    
    # 補正後の平均
    #
    
    for k in ['APP_RATE', 'NAP_RATE']:
        if args.k_days > 0:
            t0 = sn_fm_dt(d0)
            t_node = np.arange(t0, t_max(ppa) + 1, 1) # 移動平均を求める時刻
            tven_buf[k] = calc_mav(fc_dict, k, t_node, ppa, w_days=30, k_days=args.k_days)
        else:
            t0 = sn_fm_dt(d0)
            t0_sunday = t0 + (6 - d0.weekday())  # 0:月曜  6:日曜
            t_node = np.arange(t0_sunday, t_max(ppa) + 1, 7) # 移動平均を求める時刻
            tven_buf[k] = calc_every_sunday(fc_dict, k, t_node, ppa)
        
    if 1:
        proc_summary()
        proc_summary_x(ppa, fc_dict)
    
    if 1:
        # 公表値/補正値/残差
        fig, axes = plt.subplots(3, 2, figsize=(10, 7))
        fig.subplots_adjust(left=0.1, bottom=0.1, right=0.90, top=0.95, wspace=0.44)
        
        fig.text(0.20, 0.97, '支持する')
        if args.k_days > 0:
            fig.text(0.29, 0.62, '平均は指数移動平均')
            fig.text(0.29, 0.60, '(時定数 %d 日)' % args.k_days)
        else:
            fig.text(0.29, 0.62, '平均は日曜前後数日')
        proc_raw_cal_sdv(fc_dict, axes, 0, 'APP_RATE', ppa)
            
        fig.text(0.70, 0.97, '支持しない')
        if args.k_days > 0:
            fig.text(0.75, 0.62, '平均は指数移動平均')
            fig.text(0.75, 0.60, '(時定数 %d 日)' % args.k_days)
        else:
            fig.text(0.75, 0.62, '平均は日曜前後数日')
        proc_raw_cal_sdv(fc_dict, axes, 1, 'NAP_RATE', ppa)
        
        if args.gout:
             fig.savefig(os.path.join(args.gout_folder, 'Fig%d_%s.png' % (args.gout_ndx + 2, cfg['gout_date'])))
        
    if 1:
        proc_factor_mav(ppa, 'APP_RATE', '内閣 支持率 感度係数', fc_dict, 3)
        proc_factor_mav(ppa, 'NAP_RATE', '内閣 不支持率 感度係数', fc_dict, 4)
        
    # 表示
    #    イメージファイルの出力は proc_last() 内で行う
    #    複数の図を出力するアプリの plot.show() は一つなので main の最後で実施する
    if args.gout == False:
        plt.show()
        
if __name__ == '__main__':
    main()
    