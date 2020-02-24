"""  支持率 -- 不支持率  (報道 10社の平均)

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
    
def proc_raw_cal_sdv(fc_dict, axes, yn, pp, tt, pp_buf, pp_func, sdv_buf, num_buf, column):
    ax =axes[0, column]
    ax.set_ylim(20, 70)
    ax.set_ylabel('調査結果(発表値) %')
    for p in pp:
        dd = [dt_fm_sn(a) for a in p.db['T']]
        ax.plot(dd, p.db[yn], p.marker, ms=p.size*0.5, label=p.label, alpha=0.5)
    # dd = [dt_fm_sn(a) for a in tt]
    # ax.plot(dd, pp_buf[yn], '-', color='blue', lw=6, alpha=0.2)
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
        ax.plot(dd, vv, p.marker, ms=p.size*0.5, label=p.label, alpha=0.3)
    dd = [dt_fm_sn(a) for a in tt]
    # ax.plot(dd, pp_buf[yn], '-', color='blue', lw=1, alpha=1)
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
    
    dd = [dt_fm_sn(a) for a in tt]
    err = sdv_buf[yn]/np.sqrt(num_buf[yn])
    ax.plot(dd, err)
    
    set_date_tick(ax, (1, 7), '%Y/%m', 30)
    ax.grid(True)
    ax.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0))
    
def proc_summary(tta, ppa_buf, sdv_buf, num_buf):
    args = cfg['args']
    
    flg_jnn = False
    
    dda = [dt_fm_sn(a) for a in tta]
    
    fig, ax1 = plt.subplots()
    fig.subplots_adjust(left=0.16, right=0.86, bottom=0.15)
    ax1.set_title('報道 10社の平均')
    
    cy = 'darkorange'
    cy2 = 'orangered'
    cn = 'skyblue'
    cn2 = 'darkcyan'
    
    ax = ax1
    # ax.xaxis_date()
    ax.set_ylim([0, 100])
    ax.set_xlim(dt_fm_sn(tta[0]), dt_fm_sn(30 + tta[-1]))
    
    ax.fill_between(dda, np.zeros_like(ppa_buf['APP_RATE']), ppa_buf['APP_RATE'], 
            color=cy, label='報道10社平均', alpha=0.5)
    
    err = sdv_buf['APP_RATE']/np.sqrt(num_buf['APP_RATE'])
    ax.plot(dda, ppa_buf['APP_RATE']-err, color=cy, linestyle='dashed', alpha=0.7)
    ax.plot(dda, ppa_buf['APP_RATE']+err, color=cy, linestyle='dashed', alpha=0.7)
    
    ax.tick_params(axis='y', colors=cy2)
    ax.set_yticks(range(0, 51, 10))
    ax.text(datetime(2016, 9, 1), 30, '支持する', color=cy2, fontsize=20)
    ax.set_ylabel('内閣を支持する [%]', color=cy2, fontsize=14)
    ax.yaxis.set_label_coords(-0.08, 0.3)
    # ax.legend(loc='upper left', bbox_to_anchor=(0.65, 0.25))
    
    ax2 = ax1.twinx()
    ax = ax2
    ax.xaxis_date()
    ax.set_ylim([100, 0])
    ax.fill_between(dda, np.zeros_like(ppa_buf['NAP_RATE']), ppa_buf['NAP_RATE'], 
            color=cn, label='報道10社平均', alpha=0.5)
    
    err = sdv_buf['NAP_RATE']/np.sqrt(num_buf['NAP_RATE'])
    ax.plot(dda, ppa_buf['NAP_RATE']-err, color=cn, linestyle='dashed', alpha=0.7)
    ax.plot(dda, ppa_buf['NAP_RATE']+err, color=cn, linestyle='dashed', alpha=0.7)

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
    fig.text(0.19, 0.16, "平均は指数移動平均(時定数 %d 日)"%args.k_days, fontsize=8) #, bbox=bbox)
    
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
    
    def _mav(t):
        # 時刻 t における窓付き指数移動平均
        #     w_days : [day] 窓幅
        #     k_days : [day] 時定数
        #
        ndx = (_tt >= t - w_days) & (_tt <= t + w_days)
        tt = _tt[ndx]
        vv = _vv[ndx]
        ww = np.exp(-np.abs(tt - t)/k_days)
        avg = np.sum(ww*vv)/np.sum(ww)
        num = len(tt)
        return avg, num
        
    # 全社平均(指数移動平均)を求める。
    #  f_mav(t) は補間関数
    # t_node = [a for a in sorted(np.arange(t_max(db_list), t_min(db_list), -2))]
    v_node, n_node = zip(*[_mav(a) for a in t_node])
    v_node = np.array(v_node)
    
    f_mav = interp(t_node, v_node)
    
    def _err(t):
        ndx = (_tt >= t - w_days) & (_tt <= t + w_days)
        tt = _tt[ndx]
        vv = _vv[ndx]
        d = [v - f_mav(t) for t, v in zip(tt, vv)]
        return np.std(d, ddof=1)
    e_node = [_err(a) for a in t_node]
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
                help='DB の長期移動平均の窓サイズ [days]. (180)')
    
    # GOUT
    opt.add_argument('-g', '--gout', action='store_true',
                help='グラフのファイル出力')
    opt.add_argument('-f', dest='gout_folder', default='../output',
                help='グラフの出力先フォルダ (../output)')
    opt.add_argument('-n', dest='gout_ndx', type=int, default=31,
                help='グラフの(先頭)図番号 Fig# (31)')
    
    # トレンド グラフ
    opt.add_argument('-k', dest='k_days', type=int, default=10,
                help='指数移動平均の時定数[day]  (10)')
    # opt.add_argument('-t', dest='trimday', default=None,
    #            help='直近 n 日の結果を抽出 (-t14 for last 2 weeks)') 
    
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
    tta = np.arange(t0, t_max(ppa), 1) # 移動平均を求める時刻
    
    ppa_buf = {} # 移動平均 (点列)
    num_buf = {}
    sdv_buf = {}
    ppa_func = {}
    for k in ['APP_RATE', 'NAP_RATE']:
        ppa_buf[k], sdv_buf[k], num_buf[k] = calc_mav(fc_dict, k, tta, ppa, w_days=14, k_days=args.k_days)
        ppa_func[k] = interp(tta, ppa_buf[k])
    
    if 1:
        proc_summary(tta, ppa_buf, sdv_buf, num_buf)
    
    if 1:
        # 公表値/補正値/残差
        fig, axes = plt.subplots(3, 2, figsize=(10, 7))
        fig.subplots_adjust(left=0.1, bottom=0.1, right=0.90, top=0.95, wspace=0.44)
        
        fig.text(0.20, 0.97, '支持する')
        #fig.text(0.29, 0.62, '平均は指数移動平均')
        #fig.text(0.29, 0.60, '(時定数 %d 日)' % args.k_days)
        proc_raw_cal_sdv(fc_dict, axes, 'APP_RATE', ppa, tta, ppa_buf, ppa_func, sdv_buf, num_buf, 0)
            
        fig.text(0.70, 0.97, '支持しない')
        fig.text(0.75, 0.62, '平均は指数移動平均')
        fig.text(0.75, 0.60, '(時定数 %d 日)' % args.k_days)
        proc_raw_cal_sdv(fc_dict, axes, 'NAP_RATE', ppa, tta, ppa_buf, ppa_func, sdv_buf, num_buf, 1)
        
        if args.gout:
             fig.savefig(os.path.join(args.gout_folder, 'Fig%d_%s.png' % (args.gout_ndx + 2, cfg['gout_date'])))
        
    if 1:
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
        dda = [dt_fm_sn(a) for a in tta]
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
    