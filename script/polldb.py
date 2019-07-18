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
    
def load_reverse(fn):
    """ 支持率/不支持率の読み込み。
    Parameters
    ----------
    fn, str : ファイル名(フルパス)
    
    Returns
    -------
    buf, dict : 日時, 支持率, 不支持率 のリストの辞書
    
    Notes
    -----
    入力は日付の降順を仮定し、本ルーチンで昇順に直す。
    reverse しているが、日付でソートした方が良さそう。
    
    """
    def _r(s):
        return np.array([a for a in reversed(s)])
        
    data, names_ = fileio.load_core(fn)
    names = [_ for _ in names_ if _[:4] != 'DATE']
    t1 = [fileio.sn_fm_dt(_) for _ in data['DATE1']]
    t2 = [fileio.sn_fm_dt(_) for _ in data['DATE2']]
    
    buf = {k:_r(data[k]) for k in names}
    buf['T'] = _r([(a + b)/2 for (a, b) in zip(t1, t2)])
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
        self.ma = {k:MA(self.db['T'], self.db[k]) for k in self.db} # 長期移動平均
        self.interp = {k:interp(self.db['T'], self.db[k]) for k in self.db} # 直線補間

    def load(self, fn):
        a = load_reverse(os.path.join(self.data_folder, fn)) # T Y N
        ndx = (a['T'] >= fileio.sn_fm_dt(self.t0)) & (a['T'] <= fileio.sn_fm_dt(self.tf))
        buf = {k: a[k][ndx] for k in a}
        return buf
        
        
class MA:
    """ 移動平均用の関数(感度解析用)
    
    使い方
    MA.set_window(...) # MA() 共通
    f = MA([t1, t2, t3, ...], [v1, v2, v3, ...)) # 時系列から移動平均関数を生成
    v = f(t)  # 時刻 t に対応する移動平均を得る。
    
    最初にデータ期間を指定する。
    d_before days ～ d_after days のデータを使って単純移動平均。
    d_before や d_after に 180 を指定すると、前後 6 ヵ月の平均になる。
    報道各社の感度の解析に使うことを目的として、半年とか一年とかの長
    期の移動平均の関数を生成する。
    
    """
    
    step = 10 # [day] サンプリング周期
    
    @classmethod
    def set_window(kls, d_before, d_after):
        kls.d_before = d_before
        kls.d_after = d_after
        
    def __init__(self, tt, vv):
        self.f_mav = self.gen_mav(tt, vv)
        
    def __call__(self, t):
        v = self.f_mav(t)
        return v
        
    def gen_mav(self, tt, vv):
        
        def _mav(t):
            ndx = (tt >= t - self.d_before) & (tt <= t + self.d_after)
            return np.mean(vv[ndx])
            
        t_node = np.arange(tt[0], tt[-1], self.step)
        v_node = [_mav(a) for a in t_node]
        f_mav = interp(t_node, v_node)
        return f_mav
        
        
def gen_avg_fnc(fnc_list, t_node):
    """平均関数を生成する
    
    評価点 t_node 毎に fnc_list に含まれる関数の値を求めて、
    その平均値から interp1d で関数を生成する。

    Parameters
    ----------
    fnc_list, list of function : [F1(t), F2(t), ...]
    t_node, 1d-array : 評価点 t1, t2, t3, ...
    
    Returns
    -------
    avg_fnc, function : 平均関数 = (1/n)*ΣFi(t)
    
    """
    m_node = np.mean([[fnc(t) for t in t_node] for fnc in fnc_list], axis=0)
    return interp(t_node, m_node)
    
    
def gen_avg_dict(db_list):
    """ 報道各社毎の長期平均の全社平均の辞書を生成する。
    辞書の key は フィールド名('APP_RATE' 等)
    主に報道機関ごとの支持率や不支持率の感度を求めるために用いる。
    報道機関 db の感度 : 
    　　感度 = db.ma['APP_RATE'](t)/avg_dict['APP_RATE'](t)
    
    Parameters
    ----------
    db_list, list : DB() インスタンスのリスト
    
    Returns
    -------
    avg_dict, dict : 長期平均の平均の辞書
    
    Notes
    -----
    avg_dict['APP_RATE'](t) により、APP_RATE の長期平均の平均が得られる。
    報道機関 db の感度を以下で求まる。
    　　感度 = db.ma['APP_RATE'](t)/avg_dict['APP_RATE'](t)
    
    """
    avg_dict = {}
    tstp = 10 # [day]
    t_node = np.arange(t_min(db_list), t_max(db_list), tstp)
    for k in db_list[0].ma:
        fnc_list = [db.ma[k] for db in db_list]
        avg_dict[k] = gen_avg_fnc(fnc_list, t_node)
    return avg_dict
    
    