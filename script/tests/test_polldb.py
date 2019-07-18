# polldb のテスト
# 
from nose.tools import ok_, eq_
import numpy as np
from datetime import datetime, timedelta
from polldb import MA, DB, gen_avg_fnc, gen_avg_dict
import fileio

def test_MA():
    MA.set_window(150, 150)
    tt = np.array(range(0, 300, 30))
    vv = np.array([10 + a/10 for a in tt])
    ma = MA(tt, vv)
    eq_(ma(-1), ma(0))
    eq_(ma(270), ma(300))
    
def test_DB():
    MA.set_window(150, 150)
    DB.set_data_folder('../data/')
    DB.set_span(datetime(2019,1,1), datetime(2019,12,31))
    db = DB('sample.txt', 'Sample', '+', 8)
    eq_(db.db['APP_RATE'][0], 12) # 順序反転するので[0] は末尾
    
    t = fileio.sn_fm_dt(datetime(2019,2,4))
    ok_(12 < db.ma['APP_RATE'](t) < 78)

def test_gen_avg_fnc():
    tt = np.linspace(0, np.pi, 10)
    m = gen_avg_fnc([np.sin, np.cos], tt)
    for t in tt:
        m_ = (np.sin(t) + np.cos(t))/2
        ok_(abs(m(t) - m_) < 1e-3)

def test_gen_avg_dict():
    MA.set_window(150, 150)
    DB.set_data_folder('../data/')
    DB.set_span(datetime(2019,1,1), datetime(2019,12,31))
    
    db_list = [
        DB('sample.txt', 'Sample', '+', 8),
        DB('sample1.txt', 'Sample', '+', 8),
    ]
    avg_dict = gen_avg_dict(db_list)
    t = fileio.sn_fm_dt(datetime(2019, 2, 15))
    avg_dict['APP_RATE'](t)
