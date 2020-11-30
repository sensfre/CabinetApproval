"""
"""
from datetime import datetime, timedelta
from polldb import DB

_SSRC = False
#_SSRC = True

def db_defs(d0, df, data_folder):
    
    DB.set_span(d0, df) # 解析期間
    DB.set_data_folder(data_folder) # データフォルダー
    
    # グループH
    pp2 = [
          DB('nikkei.txt', '日経', '+', 10), # plus
          DB('yomiuri.txt', '読売', 'D', 6), # diamond
          DB('kyodo.txt', '共同', '1', 10),  # tickright
          DB('ssrc.txt', 'SSRC', '>', 7),   # >
          
    ]
    
    # グループL
    pp3 = [
          DB('nhk.txt', 'NHK', 'o', 7), # circle
          DB('jiji.txt', '時事', 'v', 7), # triangle_down
          DB('ann.txt', 'ANN', '2', 10), # tickup
          DB('asahi.txt', '朝日', 's', 7), # square
    ]
    # グループX
    ppj = [
          DB('jnn.txt', 'JNN', 'x', 7), # x
    ]
    
    return pp2, pp3, ppj
