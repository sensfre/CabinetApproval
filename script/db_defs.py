"""
"""
from datetime import datetime, timedelta
from polldb import MA, DB

def db_defs(d0, df, data_folder, ma_days):
    
    MA.set_window(ma_days, ma_days) # 長期移動平均のウィンドウ [days]
    
    DB.set_span(d0, df) # 解析期間
    DB.set_data_folder(data_folder) # データフォルダー
    
    
    # グループH
    pp2 = [
          DB('yomiuri.txt', '読売', 'D', 6), # diamond
          DB('nikkei.txt', '日経', '+', 10), # plus
          DB('kyodo.txt', '共同', '1', 10), # tickright
          DB('fnn.txt', 'FNN', '*', 10), # star
    ]
    # グループL
    pp3 = [
          DB('mainichi.txt', '毎日', '^', 7),
          DB('asahi.txt', '朝日', 's', 7), # square
          DB('ann.txt', 'ANN', '2', 10), # tickup
          DB('jiji.txt', '時事', 'v', 7), # triangle_down
          DB('nhk.txt', 'NHK', 'o', 7), # circle
    ]
    # グループX
    ppj = [
          DB('jnn.txt', 'JNN', 'x', 7), # x
    ]
    
    return pp2, pp3, ppj
