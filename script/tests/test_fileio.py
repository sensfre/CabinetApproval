# fileio のテスト
# 
from nose.tools import ok_, eq_

from fileio import sn_fm_dt, dt_fm_sn, load_core
from datetime import datetime, timedelta
import os

def test_sn_fm_dt():
    eq_(61, sn_fm_dt(datetime(1900, 3, 1)))
    
def test_dt_fm_sn():
    eq_(dt_fm_sn(61), datetime(1900, 3, 1))
    
def test_load_core():
    data, names = load_core('../data/sample.txt')
    
    eq_(names[0], 'DATE1')
    eq_(names[4], 'N_RESP')
    
    eq_(data[0][0], datetime(2019, 2, 3))
    eq_(data[1][4], 56)
    
    eq_(data['APP_RATE'][0], 78)
    eq_(data['N_RESP'][1], 56)
    
    eq_(data[0]['N_RESP'], data['N_RESP'][0])
