""" 2グループに分けて 支持率 -- 不支持率

"""
import os
import argparse
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from fileio import dt_fm_sn, sn_fm_dt
from polldb import DB, interp, t_min, t_max, calc_fact
from trend_util import TVEN, trend_mav, trend_sunday, deviation, set_date_tick
from db_defs import db_defs

cfg = {
    'gout_date': datetime.now().strftime('%Y%m%d'), # file 名に日付を付加する
    'args': None,    # parse_args() の戻り値を保持する
}

tven_buf = {
    'H':{},
    'L':{},
    'J':{},
}

def proc_raw_cal_sdv(fc_dict, axes, yn, db_list, tim, avg):
    
    ax =axes[0]
    ax.set_ylim(20, 70)
    ax.set_ylabel('調査結果(発表値) %')
    for db in db_list:
        dd = [dt_fm_sn(a) for a in db.db['T']]
        ax.plot(dd, db.db[yn], db.marker, ms=db.size*0.5, label=db.label, alpha=0.5)
    set_date_tick(ax, (1,4,7,10), '%m', 0)
    ax.grid(True)
    ax.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0))
    
    ax =axes[1]
    ax.set_ylim(20, 70)
    ax.set_ylabel('感度補正後(太線は平均値) %')
    for db in db_list:
        dd = [dt_fm_sn(a) for a in db.db['T']]
        ff = [fc_dict[yn][db.label](t) for t in db.db['T']]
        vv = [a/b for a, b in zip(db.db[yn], ff)]
        ax.plot(dd, vv, db.marker, ms=db.size*0.5, label=db.label, alpha=0.5)
    dd = [dt_fm_sn(a) for a in tim]
    ax.plot(dd, avg, '-', color='blue', lw=8, alpha=0.1)
    set_date_tick(ax, (1,4,7,10), '%m', 0)
    ax.grid(True)
    ax.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0))
    
    ax =axes[2]
    ax.set_ylim(-8, 8)
    ax.set_ylabel('感度補正後の残差 %')
    for db in db_list:
        vv = [a/fc_dict[yn][db.label](b) for (a, b) in zip(db.db[yn], db.db['T'])]
        ss, sd = deviation(db.db['T'], vv, interp(tim, avg))
        dd = [dt_fm_sn(a) for a in db.db['T']]
        ax.plot(dd, ss, '-', label=db.label, alpha=0.5)
    set_date_tick(ax, (1, 7), '%Y/%m', 30)
    ax.grid(True)
    ax.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0))
    
def proc_trend():
    """ サマリー  (↑支持, ↓不支持) + 円グラフ
    """
    args = cfg['args']
    flg_jnn = False
    
    tt2, app_hi, err_, num_ = tven_buf['H']['APP_RATE'].by_column()
    tt2, nap_hi, err_, num_ = tven_buf['H']['NAP_RATE'].by_column()
    tt3, app_lo, err_, num_ = tven_buf['L']['APP_RATE'].by_column()
    tt3, nap_lo, err_, num_ = tven_buf['L']['NAP_RATE'].by_column()
    ttj, app_j, err_, num_ = tven_buf['J']['APP_RATE'].by_column()
    ttj, nap_j, err_, num_ = tven_buf['J']['NAP_RATE'].by_column()
    
    dd2 = [dt_fm_sn(a) for a in tt2]
    dd3 = [dt_fm_sn(a) for a in tt3]
    ddj = [dt_fm_sn(a) for a in ttj]
    
    fig, ax1 = plt.subplots()
    fig.subplots_adjust(left=0.16, right=0.86, bottom=0.15)
    
    # 色指定
    cy = 'darkorange'
    cy2 = 'orangered'
    cn = 'skyblue'
    cn2 = 'darkcyan'
    
    ax = ax1
    if 0:
        ax.bar(dd3, app_lo, width=2, color=cy, label='グループL', alpha=0.5)
        ax.plot(dd3[-1], app_lo[-1], 'o', color='red', ms=3)
    else:
        ax.plot(dd3, app_lo, lw=1, color=cy, label='グループL', alpha=1.0)
    if flg_jnn:
        ax.plot(ddj, app_j, '--', lw=1, color=cy, label='JNN', alpha=1.0)
    ax.plot(dd2, app_hi, '-', lw=1, color='tomato', label='グループH')
    
    # Y 凡例
    ax.legend(loc='upper left', bbox_to_anchor=(0.65, 0.25))
    
    # Y 軸
    ax.set_ylim([0, 100])
    ax.tick_params(axis='y', colors=cy2)
    ax.set_yticks(range(0, 51, 10))
    ax.text(datetime(2016, 9, 1), 22, '支持する', color=cy2, fontsize=20)
    ax.set_ylabel('内閣を支持する [%]', color=cy2, fontsize=14)
    ax.yaxis.set_label_coords(-0.08, 0.3)
    
    # ---< 不支持率 >---
    ax2 = ax1.twinx()
    ax = ax2
    if 0:
        ax.bar(dd3, nap_lo, width=2, color=cn, label='グループL', alpha=0.5)
        ax.plot(dd3[-1], nap_lo[-1], 'o', color='blue', ms=2)
    else:
        ax.plot(dd3, nap_lo, lw=1, color=cn, label='グループL', alpha=1.0)
    if flg_jnn:
        ax.plot(ddj, nap_j, '--', lw=1, color=cn, label='JNN', alpha=1.0)
    ax.plot(dd2, nap_hi, '-', lw=1, color='royalblue', label='グループH')
    
    # Y2 凡例 (順序を逆転)
    hh, ll = ax.get_legend_handles_labels()
    hh, ll = reverse_legend(hh, ll)
    ax.legend(hh, ll, loc='upper left', bbox_to_anchor=(0.65, 0.9))
    
    # Y2 軸
    ax.set_ylim([100, 0])
    ax.tick_params(axis='y', colors=cn2)
    ax.set_yticks(range(0, 51, 10))
    ax.text(datetime(2016, 8, 1), 18, '支持しない', color=cn2, fontsize=20)
    ax.set_ylabel('内閣を支持しない [%]', color=cn2, fontsize=14)
    ax.yaxis.set_label_coords(1.08, 0.7)
    
    # X 軸
    ax.xaxis_date()
    ax.set_xlim(dt_fm_sn(min(tt2[0],tt3[0])), dt_fm_sn(30 + max(tt2[-1],tt3[-1])))
    set_date_tick(ax1, (1, 7), '%Y/%m', 30)
    
    # タイトル/グリッド
    ax1.grid(which='both')
    ax2.grid(which='both')
    ax1.grid(which='minor', alpha=0.1)
    ax2.grid(which='minor', alpha=0.1)
    
    # 注釈
    # bbox=dict(facecolor='white', edgecolor='none', alpha=0.7)
    fig.text(0.19, 0.23, "グループ H: 読売/日経/共同/FNN の平均", fontsize=8) #, bbox=bbox)
    fig.text(0.19, 0.19, "グループ L: 毎日/朝日/時事/ANN/NHK の平均", fontsize=8) #, bbox=bbox)
    fig.text(0.19, 0.16, "平均は指数移動平均(時定数 %d 日)"%args.k_days, fontsize=8) #, bbox=bbox)
    
    if args.gout:
        fig.savefig(os.path.join(args.gout_folder, 'Fig%d_%s.png' % (args.gout_ndx + 0, cfg['gout_date'])))
    
    # ---< 円グラフ >---
    fig = plt.figure(figsize=(4, 4))
    fig.subplots_adjust(left=0, bottom=0, right=1, top=1)
    ax = fig.add_subplot(1,1,1)
    n3=nap_lo[-1]
    n2=nap_hi[-1]
    y3=app_lo[-1]
    y2=app_hi[-1]
    dd = [n3, n2-n3, 100-n2-y2, y2-y3, y3]
    # cc = [cn, 'royalblue', '0.3', 'tomato', cy]
    # cc = [cn, 'deepskyblue', '0.3', 'orange', cy]
    cc = [cn, 'royalblue', '0.7', 'tomato', cy]
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
    
    print('L (3)', y3, n3)
    print('H (2)', y2, n2)
    
def proc_yn(pp2, pp3, ppj):
    """ 支持と不支持の合計のトレンド
    
    """
    args = cfg['args']
    
    fig, ax = plt.subplots()
    fig.subplots_adjust(right=0.8, bottom=0.15)
    ax.set_title('内閣支持率と不支持率の合計', fontsize=15)
    
    # ax.set_xlim([datetime(2016,4,1), datetime(2018,10,1)])
    for db_list in [ppj, pp2, pp3]:
        for db in db_list:
            x = [dt_fm_sn(a) for a in db.db['T']]
            y = np.array(db.db['APP_RATE']) + np.array(db.db['NAP_RATE'])
            ax.plot(x, y, db.marker + '-', ms=db.size*0.5, label=db.label)
            
    ax.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0))
    ax.grid(True)
    set_date_tick(ax, (1, 7), '%Y/%m', 30)
    ax.set_ylabel('支持率 + 不支持率 [%]', fontsize=14)
    
    if args.gout:
        fig.savefig(os.path.join(args.gout_folder, 'Fig%d_%s.png' % (args.gout_ndx + 4, cfg['gout_date'])))
    
    
def proc_fc(fc_dict, pp2, pp3, ppj):
    """ 感度係数 H, L 別
    """
    fig, axes = plt.subplots(4, 1, figsize=(6,8))
    fig.subplots_adjust(left=0.1, bottom=0.1, right=0.85, top=0.95, hspace=0.3)
    for j, (yn, db_list) in enumerate( [('APP_RATE', pp2), ('NAP_RATE', pp2), ('APP_RATE', pp3), ('NAP_RATE', pp3)]):
        ax = axes[j]
        for db in db_list:
            fc = fc_dict[yn][db.label]
            t = db.db['T']
            d = [dt_fm_sn(a) for a in t]
            f = [fc(a) for a in t]
            ax.plot(d, f, label=db.label)
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
    
def proc_hilo():
    """ HI - LO のトレンド
    """
    fig, axes = plt.subplots(2, 1)
    fig.subplots_adjust(left=0.16, right=0.86, bottom=0.15)
    for (ndx, yn) in enumerate(['APP_RATE', 'NAP_RATE']):
        tim2, avg2, _err, _num = tven_buf['H'][yn].by_column()
        tim3, avg3, _err, _num = tven_buf['L'][yn].by_column()
        f2 = interp(tim2, avg2)
        f3 = interp(tim3, avg3)
        tmin = max(tim2[0], tim3[0])
        tmax = min(tim2[-1], tim3[-1])
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
            
def reverse_legend(hh, ll):
    # zip object is not reersible...
    hhll = [a for a in zip(hh, ll)]
    hhll.reverse()
    hh, ll = zip(*hhll)
    return hh, ll
    
    
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
    
    # ファクター設定
    fc_dict = {}
    for yn in ['APP_RATE', 'NAP_RATE']:
        fc_dict[yn] = {}
        for db_list in [ppj, pp2, pp3]:
            tstp = 10
            tt = np.arange(t_min(db_list), t_max(db_list), tstp)
            ff_step = calc_fact(db_list, yn, tt, d_window=6*30)
            for db, f in zip(db_list, ff_step):
                fc_dict[yn][db.label] = interp(tt, f)
    
    # 補正後の平均
    #
    t0 = sn_fm_dt(d0)
    t_node2 = np.arange(t0, t_max(pp2) + 1, 1)
    t_node3 = np.arange(t0, t_max(pp3) + 1, 1)
    t_nodej = np.arange(t0, t_max(ppj) + 1, 1)
    
    for k in ['APP_RATE', 'NAP_RATE']:
        tven_buf['H'][k] = trend_mav(fc_dict, k, t_node2, pp2, w_days=30, k_days=args.k_days)
    
    for k in ['APP_RATE', 'NAP_RATE']:
        tven_buf['L'][k] = trend_mav(fc_dict, k, t_node3, pp3, w_days=30, k_days=args.k_days)
    
    for k in ['APP_RATE', 'NAP_RATE']:
        tven_buf['J'][k] = trend_mav(fc_dict, k, t_nodej, ppj, w_days=30, k_days=args.k_days)
    
    if 1:
        proc_trend()
    
    if 1:
        # 公表値/補正値/残差
        for yn in ['APP_RATE', 'NAP_RATE']:
            fig, axes = plt.subplots(3, 2, figsize=(10, 7))
            fig.subplots_adjust(left=0.1, bottom=0.1, right=0.90, top=0.95, wspace=0.44)
            
            fig.text(0.15, 0.97, '支持%s(グループH)' % {'APP_RATE':'する', 'NAP_RATE':'しない'}[yn])
            fig.text(0.29, 0.62, '平均は指数移動平均')
            fig.text(0.29, 0.60, '(時定数 %d 日)' % args.k_days)
            tt2, avg, err, num = tven_buf['H'][yn].by_column()
            proc_raw_cal_sdv(fc_dict, axes[:,0], yn, pp2, tt2, avg)
            
            fig.text(0.65, 0.97, '支持%s(グループL)' % {'APP_RATE':'する', 'NAP_RATE':'しない'}[yn])
            fig.text(0.75, 0.62, '平均は指数移動平均')
            fig.text(0.75, 0.60, '(時定数 %d 日)' % args.k_days)
            tt3, avg, err, num = tven_buf['L'][yn].by_column()
            proc_raw_cal_sdv(fc_dict, axes[:,1], yn, pp3, tt3, avg)
            
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
        proc_hilo()
    
    # 表示
    #    イメージファイルの出力は proc_last() 内で行う
    #    複数の図を出力するアプリの plot.show() は一つなので main の最後で実施する
    if args.gout == False:
        plt.show()
        
if __name__ == '__main__':
    main()
    