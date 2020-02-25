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
    
def proc_raw_cal_sdv(fc_dict, axes, yn, pp, _tt, _pp_buf, pp_func, _sdv_buf, _num_buf, column):
    
    tvsn = [(a,b,c,d) for (a,b,c,d) in zip(_tt, _pp_buf[yn], _sdv_buf[yn], _num_buf[yn]) if d > 0]
    tt, pp_buf, sdv_buf, num_buf = [np.array(a) for a in zip(*tvsn)]
    
    ax =axes[0, column]
    ax.set_ylim(20, 70)
    ax.set_ylabel('調査結果(発表値) %')
    for p in pp:
        dd = [dt_fm_sn(a) for a in p.db['T']]
        ax.plot(dd, p.db[yn], p.marker, ms=p.size*0.5, label=p.label, alpha=0.5)
    # dd = [dt_fm_sn(a) for a in tt]
    # ax.plot(dd, pp_buf[yn], '-', color='blue', lw=6, alpha=0.2) # 平均値
    set_date_tick(ax, (1,4,7,10), '%m', 0)
    ax.grid(True)
    ax.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0))
    
    ax =axes[1, column]
    ax.set_ylim(20, 70)
    ax.set_ylabel('感度補正後(曲線は平均値) %')
    ax.set_ylabel('感度補正後 %')
    for p in pp:
        dd = [dt_fm_sn(a) for a in p.db['T']]
        ff = [fc_dict[yn][p.label](t) for t in p.db['T']]
        vv = [a/b for a, b in zip(p.db[yn], ff)]
        ax.plot(dd, vv, p.marker, ms=p.size*0.5, label=p.label, alpha=0.5)
    dd = [dt_fm_sn(a) for a in tt]
    e = sdv_buf/np.sqrt(num_buf)
    ax.fill_between(dd, pp_buf-e, pp_buf+e, color='blue', alpha=0.1)
    ax.plot(dd, pp_buf,'-', color='blue', lw=1, alpha=1)
    set_date_tick(ax, (1,4,7,10), '%m', 0)
    ax.grid(True)
    #ax.legend(loc='upper left', bbox_to_anchor=(1.0, 1.1))
    
    ax =axes[2, column]
    ax.set_ylim(-8, 8)
    ax.set_ylabel('感度補正後の残差 %')
    for p in pp:
        alpha = 0.5
        ff = [fc_dict[yn][p.label](t) for t in p.db['T']]
        vv = [a/b for a, b in zip(p.db[yn], ff)]
        ss, sd = deviation(p.db['T'], vv, pp_func[yn])
        dd = [dt_fm_sn(a) for a in p.db['T']]
        ax.plot(dd, ss, '-', label=p.label, alpha=alpha)
    
    #dd = [dt_fm_sn(a) for a in tt]
    #err = sdv_buf/np.sqrt(num_buf)
    #ax.plot(dd, err)
    
    set_date_tick(ax, (1, 7), '%Y/%m', 30)
    ax.grid(True)
    ax.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0))
    
def proc_summary(_tta, _ppa_buf, _sdv_buf, _num_buf):
    
    
    args = cfg['args']
    
    flg_jnn = False
    
    
    fig, ax1 = plt.subplots()
    fig.subplots_adjust(left=0.16, right=0.86, bottom=0.15)
    ax1.set_title('報道 10社の平均')
    
    cy = 'darkorange'
    cy2 = 'orangered'
    cn = 'skyblue'
    cn2 = 'darkcyan'
    
    yn = 'APP_RATE'
    tvsn = [(a,b,c,d) for (a,b,c,d) in zip(_tta, _ppa_buf[yn], _sdv_buf[yn], _num_buf[yn]) if d > 0]
    tta, ppa_buf, sdv_buf, num_buf = [np.array(a) for a in zip(*tvsn)]
    dda = [dt_fm_sn(a) for a in tta]
    
    ax = ax1
    # ax.xaxis_date()
    ax.set_ylim([0, 100])
    ax.set_xlim(dt_fm_sn(tta[0]), dt_fm_sn(30 + tta[-1]))
    
    err = sdv_buf/np.sqrt(num_buf)
    ax.fill_between(dda, ppa_buf-err, ppa_buf+err, color=cy, linestyle='dashed', alpha=0.3)
    ax.plot(dda, ppa_buf, color=cy, label='報道10社平均', alpha=1)
    
    ax.tick_params(axis='y', colors=cy2)
    ax.set_yticks(range(0, 51, 10))
    ax.text(datetime(2016, 9, 1), 30, '支持する', color=cy2, fontsize=20)
    ax.set_ylabel('内閣を支持する [%]', color=cy2, fontsize=14)
    ax.yaxis.set_label_coords(-0.08, 0.3)
    # ax.legend(loc='upper left', bbox_to_anchor=(0.65, 0.25))
    

    yn = 'NAP_RATE'
    tvsn = [(a,b,c,d) for (a,b,c,d) in zip(_tta, _ppa_buf[yn], _sdv_buf[yn], _num_buf[yn]) if d > 0]
    tta, ppa_buf, sdv_buf, num_buf = [np.array(a) for a in zip(*tvsn)]
    dda = [dt_fm_sn(a) for a in tta]
    
    ax2 = ax1.twinx()
    ax = ax2
    ax.xaxis_date()
    ax.set_ylim([100, 0])
    err = sdv_buf/np.sqrt(num_buf)
    ax.fill_between(dda, ppa_buf-err, ppa_buf+err, color=cn, linestyle='dashed', alpha=0.3)
    ax.plot(dda, ppa_buf, color=cn, label='報道10社平均', alpha=1)

    ax.tick_params(axis='y', colors=cn2)
    ax.set_yticks(range(0, 51, 10))
    ax.text(datetime(2016, 8, 1), 20, '支持しない', color=cn2, fontsize=20)
    ax.set_ylabel('内閣を支持しない [%]', color=cn2, fontsize=14)
    ax.yaxis.set_label_coords(1.08, 0.7)
    hh, ll = ax.get_legend_handles_labels()
    hh, ll = reverse_legend(hh, ll)
    # ax.legend(hh, ll, loc='upper left', bbox_to_anchor=(0.65, 0.9))
    
    set_date_tick(ax1, (1, 7), '%Y/%m', 30)
    ax1.grid(which='both')
    ax2.grid(which='both')
    ax1.grid(which='minor', alpha=0.1)
    ax2.grid(which='minor', alpha=0.1)

    bbox=dict(facecolor='white', edgecolor='none', alpha=0.7)
    
    if args.gout:
        fig.savefig(os.path.join(args.gout_folder, 'Fig%d_%s.png' % (args.gout_ndx + 0, cfg['gout_date'])))
    
def proc_summary_x(_tta, _ppa_buf, _sdv_buf, _num_buf, db_list, fc_dict):
    args = cfg['args']
    flg_jnn = False
    fig, ax1 = plt.subplots(figsize=(8, 5))
    fig.subplots_adjust(left=0.16, right=0.8, bottom=0.15)
    ax1.set_title('報道 10社の平均')
    cy = 'darkorange'
    cy2 = 'orangered'
    cn = 'skyblue'
    cn2 = 'darkcyan'

    yn = 'APP_RATE'
    tvsn = [(a,b,c,d) for (a,b,c,d) in zip(_tta, _ppa_buf[yn], _sdv_buf[yn], _num_buf[yn]) if d > 0]
    tta, ppa_buf, sdv_buf, num_buf = [np.array(a) for a in zip(*tvsn)]
    dda = [dt_fm_sn(a) for a in tta]
    
    ax = ax1
    err = sdv_buf/np.sqrt(num_buf)
    ax.fill_between(dda, ppa_buf-err, ppa_buf+err, color=cy, linestyle='dashed', alpha=0.3)
    ax.plot(dda, ppa_buf, color=cy, label='支持(平均)', alpha=1)
    
    ax.set_yticks(range(0, 100, 5))
    ax.set_yticks(range(0, 100, 1), minor=True)
    ax.set_ylim([25, 60])
    
    yn = 'NAP_RATE'
    tvsn = [(a,b,c,d) for (a,b,c,d) in zip(_tta, _ppa_buf[yn], _sdv_buf[yn], _num_buf[yn]) if d > 0]
    tta, ppa_buf, sdv_buf, num_buf = [np.array(a) for a in zip(*tvsn)]
    dda = [dt_fm_sn(a) for a in tta]
    
    err = sdv_buf/np.sqrt(num_buf)
    ax.fill_between(dda, ppa_buf-err, ppa_buf+err, color=cn, linestyle='dashed', alpha=0.3)
    ax.plot(dda, ppa_buf, color=cn, label='不支持(平均)', alpha=1)
    
    ax.xaxis_date()
    ax.set_xlim(dt_fm_sn(tta[0]), dt_fm_sn(30 + tta[-1]))
    ax.set_xlim(datetime(2019,2,1), datetime(2020,4,1))
    set_date_tick(ax1, (1, 7), '%Y/%m', 30)
    ax.grid(which='both')
    ax.grid(which='minor', alpha=0.1)
    
    for db in db_list:
        yy = [a/fc_dict['APP_RATE'][db.label](b) for a,b in zip(db.db['APP_RATE'], db.db['T'])]
        dd = [dt_fm_sn(a) for a in db.db['T']]
        ax.plot(dd, yy, db.marker, ms=db.size*0.5, color='orange', alpha=1, label=db.label)
    ax.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0))
    
    if args.gout:
        fig.savefig(os.path.join(args.gout_folder, 'Fig%d_%s.png' % (args.gout_ndx + 0, cfg['gout_date'])))
    
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

def reverse_legend(hh, ll):
    # zip object is not reersible...
    hhll = [a for a in zip(hh, ll)]
    hhll.reverse()
    hh, ll = zip(*hhll)
    return hh, ll
    
    
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
            e = 3.5/2 # [pt]  1σ相当
        else:
            v = np.mean(vv)
            e = max(np.std(vv-v, ddof=1), 3.5/2/np.sqrt(n))
        return v, e, n
        
    v_node, e_node, n_node = zip(*[_avg(t) for t in t_node])
    v_node = np.array(v_node)
    e_node = np.array(e_node)
    n_node = np.array(n_node)
    
    return v_node, e_node, n_node
    
def proc_factor_mav(db_list, k_app_nap, k_title, fc_dict):
    """
    Parameters
    ----------
    db_list, list of DB()
    k_app_nap, string : 分析データキー ('APP_RATE' or 'NAP_RATE')
    k_title, string : グラフタイトル
    
    """
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
    opt.add_argument('-n', dest='gout_ndx', type=int, default=31,
                help='グラフの(先頭)図番号 Fig# (31)')
    
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
    pp2, pp3, ppj = db_defs(d0, df, args.db_folder, args.ma_days)
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
    t0 = sn_fm_dt(d0)
    t0_sunday = t0 + (6 - d0.weekday())  # 0:月曜  6:日曜
    t_node = np.arange(t0_sunday, t_max(ppa) + 1, 7) # 移動平均を求める時刻
    
    ppa_buf = {} # 移動平均 (点列)
    num_buf = {}
    sdv_buf = {}
    ppa_func = {}
    for k in ['APP_RATE', 'NAP_RATE']:
        ppa_buf[k], sdv_buf[k], num_buf[k] = calc_every_sunday(fc_dict, k, t_node, ppa)
        ppa_func[k] = interp(t_node, ppa_buf[k])
    
    if 1:
        proc_summary(t_node, ppa_buf, sdv_buf, num_buf)
        proc_summary_x(t_node, ppa_buf, sdv_buf, num_buf, ppa, fc_dict)
    
    if 1:
        # 公表値/補正値/残差
        fig, axes = plt.subplots(3, 2, figsize=(10, 7))
        fig.subplots_adjust(left=0.1, bottom=0.1, right=0.90, top=0.95, wspace=0.44)
        
        fig.text(0.20, 0.97, '支持する')
        proc_raw_cal_sdv(fc_dict, axes, 'APP_RATE', ppa, t_node, ppa_buf, ppa_func, sdv_buf, num_buf, 0)
            
        fig.text(0.70, 0.97, '支持しない')
        proc_raw_cal_sdv(fc_dict, axes, 'NAP_RATE', ppa, t_node, ppa_buf, ppa_func, sdv_buf, num_buf, 1)
        
        if args.gout:
             fig.savefig(os.path.join(args.gout_folder, 'Fig%d_%s.png' % (args.gout_ndx + 2, cfg['gout_date'])))
        
    if 0:
        proc_factor_mav(ppa, 'APP_RATE', '内閣 支持率 感度係数', fc_dict)
        proc_factor_mav(ppa, 'NAP_RATE', '内閣 不支持率 感度係数', fc_dict)
        
    if 0:
        fig, axes = plt.subplots(3, 1, figsize=(10, 7))
        # fig.subplots_adjust(left=0.1, bottom=0.1, right=0.90, top=0.95, wspace=0.44)
        for p in ppa:
            ff = [fc_dict['APP_RATE'][p.label](t) for t in p.db['T']]
            yy = [a/b for a, b in zip(p.db['APP_RATE'], ff)]
            dd = [dt_fm_sn(a) for a in p.db['T']]
            axes[0].plot(dd, yy, p.marker, ms=p.size*0.5, alpha=0.5)
        dda = [dt_fm_sn(a) for a in t_node]
        ser = sdv_buf['APP_RATE']/np.sqrt(num_buf['APP_RATE'])
        axes[0].fill_between(dda,
            ppa_buf['APP_RATE']-2*ser,
            ppa_buf['APP_RATE']+2*ser,
            alpha=0.3)
        axes[0].plot(dda, ppa_buf['APP_RATE'])
        axes[1].plot(dda, num_buf['APP_RATE'])
        axes[2].plot(dda, sdv_buf['APP_RATE'])
        axes[2].plot(dda, 2*ser)
        set_date_tick(axes[0], (1, 7), '%m', 0)
        set_date_tick(axes[1], (1, 7), '%m', 0)
        set_date_tick(axes[2], (1, 7), '%Y/%m', 30)
        axes[0].grid(True)

    # 表示
    #    イメージファイルの出力は proc_last() 内で行う
    #    複数の図を出力するアプリの plot.show() は一つなので main の最後で実施する
    if args.gout == False:
        plt.show()
        
if __name__ == '__main__':
    main()
    