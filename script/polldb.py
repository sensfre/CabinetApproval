"""polldb.py
"""
import os
from datetime import datetime, timedelta
import numpy as np
from scipy.interpolate import interp1d
import fileio

def interp(xx, yy):
    # 範囲外で返す fill_value を有効にするには、
    # bounds_error を設定する必要がある。
    return interp1d(xx, yy, fill_value=(yy[0], yy[-1]), bounds_error=False)
    
def t_max(pp):
    return max([max(p.db['T']) for p in pp])

def t_min(pp):
    return min([min(p.db['T']) for p in pp])
    
def load_sorted(fn):
    """ 支持率/不支持率の読み込み。
    Parameters
    ----------
    fn, str : ファイル名(フルパス)
    
    Returns
    -------
    buf, dict : 日時, 支持率, 不支持率 のリストの辞書
    
    Notes
    -----
    各リストは日付順にソートしている
    
    """
    data, names_ = fileio.load_core(fn)
    names = [_ for _ in names_ if _[:4] != 'DATE']
    data = data[np.argsort(data['DATE1'])] # 日付でソート
    
    t1 = [fileio.sn_fm_dt(_) for _ in data['DATE1']]
    t2 = [fileio.sn_fm_dt(_) for _ in data['DATE2']]
    buf = {k:data[k] for k in names}
    buf['T'] = np.array([(a + b)/2 for (a, b) in zip(t1, t2)])
    return buf
    
class DB:
    """ 調査結果を保持する。
    
    以下を提供する。
        日付     .db['T'][0..n]
        発表値   .db['APP_RATE'][0..n], .db['NAP_RATE'][0..n], ...
        長期平均 .ma['APP_RATE'](t), .ma['NAP_RATE'](t), ...
    
    有効期間とデータフォルダーを指定してから使う。
    set_data_folder(), set_span() を参照。
    
    グラフ属性(識別名(ラベル), マーカー, 色)も保持しているが、
    もう一段上の階層に移した方が良さそう。
    
    """
    data_folder = None # データフォルダー '../data'
    t0 = None # 分析期間 開始 (datetime インスタンス)
    tf = None #          終了
    
    @classmethod
    def set_data_folder(kls, data_folder):
        # 分析期間設定 (インスタンス共通)
        # 
        kls.data_folder = data_folder
        
    @classmethod
    def set_span(kls, t0, tf):
        # 分析期間設定 (インスタンス共通)
        # 
        kls.t0 = t0
        kls.tf = tf
        
    def __init__(self, fn, label, marker, size, color='black'):
        #
        self.fn = fn # ファイル名
        self.label = label # グラフのラベル
        self.marker = marker # グラフのマーカー
        self.size = size # マーカーの相対サイズ
        self.color = color # グラフの色
        self.db = self.load(fn)
        self.interp = {k:interp(self.db['T'], self.db[k]) for k in self.db} # 直線補間(動画で利用)

    def load(self, fn):
        a = load_sorted(os.path.join(self.data_folder, fn)) # T Y N
        ndx = (a['T'] >= fileio.sn_fm_dt(self.t0)) & (a['T'] <= fileio.sn_fm_dt(self.tf))
        buf = {k: a[k][ndx] for k in a}
        return buf
        
        
def calc_fact(db_list, k_app_nap, t_node, d_window):
    """ 各社の感度を求める
    
    Parameters
    ----------
    t_node, 1d-array : 感度係数を求める日付のリスト
    d_window, float [day] : 移動平均の窓幅 (過去 d_window 日に含まれる調査の平均を求める)
    
    Note
    ----
    ウィンドウ内の調査結果が 2 個未満の時は、感度の値を nan にする。
    
    """
    def _mav(db, t):
        ndx = (t - d_window <= db.db['T']) & (db.db['T'] <= t)
        y_ = db.db[k_app_nap][ndx]
        if len(y_) >= 2:
            ans = np.mean(y_)
        else:
            ans = np.NaN
        return ans
    
    yy = [[_mav(db, t) for t in t_node] for db in db_list]
    ya = [np.nanmean(a) for a in zip(*yy)]
    ff = [[a/b for a,b in zip(y, ya)] for y in yy]
    return ff

