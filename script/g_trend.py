""" 2グループに分けて 支持率 -- 不支持率

"""
import os
import argparse
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from fileio import dt_fm_sn, sn_fm_dt
from polldb import DB, interp, t_min, t_max
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
    
def proc_raw_cal_sdv(fc_dict, axes, yn, pp, tt, pp_buf, pp_func, column):
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
    ax.set_ylabel('感度補正後(太線は平均値) %')
    for p in pp:
        dd = [dt_fm_sn(a) for a in p.db['T']]
        ff = [fc_dict[yn][p.label](t) for t in p.db['T']]
        vv = [a/b for a, b in zip(p.db[yn], ff)]
        ax.plot(dd, vv, p.marker, ms=p.size*0.5, label=p.label, alpha=0.5)
    dd = [dt_fm_sn(a) for a in tt]
    ax.plot(dd, pp_buf[yn], '-', color='blue', lw=8, alpha=0.1)
    set_date_tick(ax, (1,4,7,10), '%m', 0)
    ax.grid(True)
    ax.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0))
    
    ax =axes[2, column]
    ax.set_ylim(-8, 8)
    ax.set_ylabel('感度補正後の残差 %')
    for p in pp:
        ff = [fc_dict[yn][p.label](t) for t in p.db['T']]
        vv = [a/b for a, b in zip(p.db[yn], ff)]
        ss, sd = deviation(p.db['T'], vv, pp_func[yn])
        dd = [dt_fm_sn(a) for a in p.db['T']]
        ax.plot(dd, ss, '-', label=p.label, alpha=alpha)
    set_date_tick(ax, (1, 7), '%Y/%m', 30)
    ax.grid(True)
    ax.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0))
    
def proc_summary(tt2, tt3, ttj, pp2_buf, pp3_buf, ppj_buf):
    args = cfg['args']
    
    flg_jnn = False
    
    dd2 = [dt_fm_sn(a) for a in tt2]
    dd3 = [dt_fm_sn(a) for a in tt3]
    ddj = [dt_fm_sn(a) for a in ttj]
    
    fig, ax1 = plt.subplots()
    fig.subplots_adjust(left=0.16, right=0.86, bottom=0.15)
    
    cy = 'darkorange'
    cy2 = 'orangered'
    cn = 'skyblue'
    cn2 = 'darkcyan'
    
    ax = ax1
    # ax.xaxis_date()
    ax.set_ylim([0, 100])
    ax.set_xlim(dt_fm_sn(min(tt2[0],tt3[0])), dt_fm_sn(30 + max(tt2[-1],tt3[-1])))
    
    ax.bar(dd3, pp3_buf['APP_RATE'], width=2, color=cy, label='グループL', alpha=0.5)
    if flg_jnn:
        ax.plot(ddj, ppj_buf['APP_RATE'], '--', lw=1, color=cy, label='JNN', alpha=1.0)
    ax.plot(dd2, pp2_buf['APP_RATE'], '-', lw=3, color='tomato', label='グループH')
    ax.tick_params(axis='y', colors=cy2)
    ax.set_yticks(range(0, 51, 10))
    ax.text(datetime(2016, 9, 1), 30, '支持する', color=cy2, fontsize=20)
    ax.set_ylabel('内閣を支持する [%]', color=cy2, fontsize=14)
    ax.yaxis.set_label_coords(-0.08, 0.3)
    ax.legend(loc='upper left', bbox_to_anchor=(0.65, 0.25))
    
    ax2 = ax1.twinx()
    ax = ax2
    ax.xaxis_date()
    ax.set_ylim([100, 0])
    ax.bar(dd3, pp3_buf['NAP_RATE'], width=2, color=cn, label='グループL', alpha=0.5)
    if flg_jnn:
        ax.plot(ddj, ppj_buf['NAP_RATE'], '--', lw=1, color=cn, label='JNN', alpha=1.0)
    ax.plot(dd2, pp2_buf['NAP_RATE'], '-', lw=3, color='royalblue', label='グループH')
    ax.tick_params(axis='y', colors=cn2)
    ax.set_yticks(range(0, 51, 10))
    ax.text(datetime(2016, 8, 1), 20, '支持しない', color=cn2, fontsize=20)
    ax.set_ylabel('内閣を支持しない [%]', color=cn2, fontsize=14)
    ax.yaxis.set_label_coords(1.08, 0.7)
    hh, ll = ax.get_legend_handles_labels()
    hh, ll = reverse_legend(hh, ll)
    ax.legend(hh, ll, loc='upper left', bbox_to_anchor=(0.65, 0.9))
    
    set_date_tick(ax1, (1, 7), '%Y/%m', 30)
    ax1.grid(which='both')
    ax2.grid(which='both')
    ax1.grid(which='minor', alpha=0.1)
    ax2.grid(which='minor', alpha=0.1)

    bbox=dict(facecolor='white', edgecolor='none', alpha=0.7)
    fig.text(0.19, 0.23, "グループ H: 読売/日経/共同/FNN の平均", fontsize=8) #, bbox=bbox)
    fig.text(0.19, 0.19, "グループ L: 毎日/朝日/時事/ANN/NHK の平均", fontsize=8) #, bbox=bbox)
    fig.text(0.19, 0.16, "平均は指数移動平均(時定数 %d 日)"%args.k_days, fontsize=8) #, bbox=bbox)
    
    if args.gout:
        fig.savefig(os.path.join(args.gout_folder, 'Fig%d_%s.png' % (args.gout_ndx + 0, cfg['gout_date'])))
    
    fig = plt.figure(figsize=(4, 4))
    fig.subplots_adjust(left=0, bottom=0, right=1, top=1)
    ax = fig.add_subplot(1,1,1)
    n3=pp3_buf['NAP_RATE'][-1]
    n2=pp2_buf['NAP_RATE'][-1]
    y2=pp2_buf['APP_RATE'][-1]
    y3=pp3_buf['APP_RATE'][-1]
    dd = [n3, n2-n3, 100-n2-y2, y2-y3, y3]
    cc = [cn, 'royalblue', '0.3', 'tomato', cy]
    ll = ['支持しない', 'やや', '他', 'やや', '支持する']
    ll = ['', 'やや', '他', 'やや', '']
    patches, texts = ax.pie(dd, labels=ll, counterclock=False, startangle=90,
        colors=cc, labeldistance=0.7,
        textprops={'color':'white'},
        radius=1.23)
    ax.text(  0.6, 0.02, '支持しない', fontsize=24, color='white', horizontalalignment='center')
    ax.text( -0.6, 0.02, '支持する',   fontsize=24, color='white', horizontalalignment='center')
    for t in texts:
        t.set_horizontalalignment('center')
        t.set_size(14)
	
    if args.gout:
        fig.savefig(os.path.join(args.gout_folder, 'Fig%d_%s.png' % (args.gout + 1, cfg['gout_date'])))
    
    print('3', pp3_buf['APP_RATE'][-1], pp3_buf['NAP_RATE'][-1])
    print('2', pp2_buf['APP_RATE'][-1], pp2_buf['NAP_RATE'][-1])
    
def proc_yn(pp2, pp3, ppj):
    args = cfg['args']
    
    fig, ax = plt.subplots()
    fig.subplots_adjust(right=0.8, bottom=0.15)
    ax.set_title('内閣支持率と不支持率の合計', fontsize=15)
    
    # ax.set_xlim([datetime(2016,4,1), datetime(2018,10,1)])
    for pp in [ppj, pp2, pp3]:
        for p in pp:
            x = [dt_fm_sn(a) for a in p.db['T']]
            y = np.array(p.db['APP_RATE']) + np.array(p.db['NAP_RATE'])
            ax.plot(x, y, p.marker + '-', ms=4, label=p.label)
            
    ax.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0))
    ax.grid(True)
    set_date_tick(ax, (1, 7), '%Y/%m', 30)
    ax.set_ylabel('支持率 + 不支持率 [%]', fontsize=14)
    
    if args.gout:
        fig.savefig(os.path.join(args.gout_folder, 'Fig%d_%s.png' % (args.gout_ndx + 4, cfg['gout_date'])))
    
    
def proc_fc(fc_dict, pp2, pp3, ppj):
    fig, axes = plt.subplots(4, 1, figsize=(6,8))
    fig.subplots_adjust(left=0.1, bottom=0.1, right=0.85, top=0.95, hspace=0.3)
    for j, (yn, pp) in enumerate( [('APP_RATE', pp2), ('NAP_RATE', pp2), ('APP_RATE', pp3), ('NAP_RATE', pp3)]):
        ax = axes[j]
        for p in pp:
            fc = fc_dict[yn][p.label]
            t = p.db['T']
            d = [dt_fm_sn(a) for a in t]
            f = [fc(a) for a in t]
            ax.plot(d, f, label=p.label)
        ax.set_ylim(0.9, 1.2)
        ax.grid(True)
        if (j % 2) == 0:
            ax.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0))
        else:
            pass
        if j == 3:
            set_date_tick(ax, (1, 7), '%Y/%m', 30)
        else:
            set_date_tick(ax, (1,4,7,10), '%m', 0)
    
def proc_hilo(tt2, tt3, ttj, pp2_buf, pp3_buf, ppj_buf):
    flg_jnn = False
    
    dd2 = [dt_fm_sn(a) for a in tt2]
    dd3 = [dt_fm_sn(a) for a in tt3]
    ddj = [dt_fm_sn(a) for a in ttj]
    
    fig, axes = plt.subplots(2, 1)
    fig.subplots_adjust(left=0.16, right=0.86, bottom=0.15)
    
    for (ndx, yn) in enumerate(['APP_RATE', 'NAP_RATE']):
        f2 = interp(tt2, pp2_buf[yn])
        f3 = interp(tt3, pp3_buf[yn])
        tmin = max(tt2[0], tt3[0])
        tmax = min(tt2[-1], tt3[-1])
        t_node = np.arange(tmin, tmax, 1)
        d_node = [dt_fm_sn(a) for a in t_node]
        y_node = [f2(t) - f3(t) for t in t_node]
        axes[ndx].plot(d_node, y_node)
        axes[ndx].grid(True)
        axes[ndx].set_ylim(-4, 12)
        if ndx == 0:
            set_date_tick(axes[ndx], (1,4,7,10), '%m', 0)
        else:
            set_date_tick(axes[ndx], (1, 7), '%Y/%m', 30)
            
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
        ans = np.sum(ww*vv)/np.sum(ww)
        return ans
        
    # 全社平均(指数移動平均)を求める。
    #  f_mav(t) は補間関数
    # t_node = [a for a in sorted(np.arange(t_max(db_list), t_min(db_list), -2))]
    v_node = np.array([_mav(a) for a in t_node])
    return v_node
    
    
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
    opt.add_argument('-n', dest='gout_ndx', type=int, default=1,
                help='グラフの(先頭)図番号 Fig# (1)')
    
    # トレンド グラフ
    opt.add_argument('-k', dest='k_days', type=int, default=10,
                help='指数移動平均の時定数[day]  (10)')
    # opt.add_argument('-t', dest='trimday', default=None,
    #            help='直近 n 日の結果を抽出 (-t14 for last 2 weeks)') 
    
    return opt
    
def calc_fact(db_list, yn):
    
    tstp = 10
    tt = np.arange(t_min(db_list), t_max(db_list), tstp)
    ma_ = interp(tt, [np.mean([db.ma[yn](t) for db in db_list]) for t in tt])
    fc_list = []
    for db in db_list:
        ff = [db.ma[yn](t)/ma_(t) for t in tt]
        fc_list.append(interp(tt, ff))
    # fc_list = [interp(tt, [db.ma[yn](t)/ma_(t) for t in tt]) for db in db_list]
    return fc_list
    
    
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
    
    # ファクター設定
    fc_dict = {}
    for yn in ['APP_RATE', 'NAP_RATE']:
        fc_dict[yn] = {}
        for pp in [ppj, pp2, pp3]:
            ff = calc_fact(pp, yn)
            for p, f in zip(pp, ff):
                fc_dict[yn][p.label] = f
    
    # 補正後の平均
    #
    t0 = sn_fm_dt(d0)
    tt2 = np.arange(t0, t_max(pp2), 1)
    tt3 = np.arange(t0, t_max(pp3), 1)
    ttj = np.arange(t0, t_max(ppj), 1)
    
    pp2_buf = {}
    pp2_func = {}
    for k in ['APP_RATE', 'NAP_RATE']:
        pp2_buf[k] = calc_mav(fc_dict, k, tt2, pp2, w_days=30, k_days=args.k_days)
        pp2_func[k] = interp(tt2, pp2_buf[k])
    
    pp3_buf = {}
    pp3_func = {}
    for k in ['APP_RATE', 'NAP_RATE']:
        pp3_buf[k] = calc_mav(fc_dict, k, tt3, pp3, w_days=30, k_days=args.k_days)
        pp3_func[k] = interp(tt3, pp3_buf[k])
    
    ppj_buf = {}
    ppj_func = {}
    for k in ['APP_RATE', 'NAP_RATE']:
        ppj_buf[k] = calc_mav(fc_dict, k, ttj, ppj, w_days=30, k_days=args.k_days)
        ppj_func[k] = interp(ttj, ppj_buf[k])
    
    if 1:
        proc_summary(tt2, tt3, ttj, pp2_buf, pp3_buf, ppj_buf)
    
    if 1:
        # 公表値/補正値/残差
        for yn in ['APP_RATE', 'NAP_RATE']:
            fig, axes = plt.subplots(3, 2, figsize=(10, 7))
            fig.subplots_adjust(left=0.1, bottom=0.1, right=0.90, top=0.95, wspace=0.44)
            
            fig.text(0.15, 0.97, '支持%s(グループH)' % {'APP_RATE':'する', 'NAP_RATE':'しない'}[yn])
            fig.text(0.29, 0.62, '平均は指数移動平均')
            fig.text(0.29, 0.60, '(時定数 %d 日)' % args.k_days)
            proc_raw_cal_sdv(fc_dict, axes, yn, pp2, tt2, pp2_buf, pp2_func, 0)
            
            fig.text(0.65, 0.97, '支持%s(グループL)' % {'APP_RATE':'する', 'NAP_RATE':'しない'}[yn])
            fig.text(0.75, 0.62, '平均は指数移動平均')
            fig.text(0.75, 0.60, '(時定数 %d 日)' % args.k_days)
            proc_raw_cal_sdv(fc_dict, axes, yn, pp3, tt3, pp3_buf, pp3_func, 1)
            
            if args.gout:
                if yn == 'APP_RATE':
                    fig.savefig(os.path.join(args.gout_folder, 'Fig%d_%s.png' % (args.gout_ndx + 2, cfg['gout_date'])))
                else:
                    fig.savefig(os.path.join(args.gout_folder, 'Fig%d_%s.png' % (args.gout_ndx + 3, cfg['gout_date'])))
    
    if 1:
        proc_yn(pp2, pp3, ppj)
        
    if 1:
        proc_fc(fc_dict, pp2, pp3, ppj)
        
    if 1:
        proc_hilo(tt2, tt3, ttj, pp2_buf, pp3_buf, ppj_buf)
    
    # 表示
    #    イメージファイルの出力は proc_last() 内で行う
    #    複数の図を出力するアプリの plot.show() は一つなので main の最後で実施する
    if args.gout == False:
        plt.show()
        
if __name__ == '__main__':
    main()
    