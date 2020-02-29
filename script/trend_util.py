""" 
"""
import numpy as np
import matplotlib.dates as mdates

from polldb import DB, interp, t_min, t_max

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
        
    
def trend_mav(fc_dict, yn, t_node, db_list, w_days, k_days):
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
    
    
def trend_sunday(fc_dict, yn, t_node, db_list):
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


def deviation(tt, yy, yi):
    yc = np.array([yi(t) for t in tt])
    yd = yy - yc
    sd = np.std(yd, ddof=1)
    return yd, sd
    
    
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
    
