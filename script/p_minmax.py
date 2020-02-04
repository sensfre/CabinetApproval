import os
import glob
from fileio import load_core
import numpy as np

def sub(fn, app_nap, mm):
    data, names = load_core(fn)
    if mm == 'min':
        j = data[app_nap].argmin()
    else:
        j = data[app_nap].argmax()
    r = data[j]
    d1 = r[0].strftime('%Y-%m-%d')
    print('%-12s %2d %s %5.1f %5.1f %6.0f' % (
        os.path.basename(fn), j, d1, r[2], r[3], r[4]))
    
def proc(app_nap, mm):
    ff = glob.glob('f:/github/sensfre/CabinetApproval/data/*.txt')
    print('%s  %s' % (app_nap, mm))
    for f in ff:
        if os.path.basename(f)[:6] == 'sample':
            pass
        else:
            sub(f, app_nap, mm)
    print()
    
def main():
    proc('NAP_RATE', 'min')
    proc('NAP_RATE', 'max')
    proc('APP_RATE', 'max')
    proc('APP_RATE', 'min')
    
main()
