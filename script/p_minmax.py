import glob
import os
import numpy as np

def load(fn):
    f = open(fn)
    buf = []
    while 1:
        xx = f.readline()
        if not xx: break
        if xx == '': continue
        x = xx.strip().split()
        if xx[0] == '#': continue
        if (x[0].strip())[:4] == 'DATE': continue
        buf.append([x[0], x[1], float(x[2]), float(x[3])])
    return np.array(buf)
    
def sub(fn, yn, mm):
    ndx = {'Y':2, 'N':3}[yn]
    aa = load(fn)
    rr = aa[:, ndx]
    if mm == 'min':
        j = rr.argmin()
    else:
        j = rr.argmax()
    print('%-12s %2d %-40s' % (os.path.basename(fn), j, aa[j]))
    
def proc(yn, mm):
    ff = glob.glob('f:/github/sensfre/CabinetApproval/data/*.txt')
    print('%s  %s' % (yn, mm))
    for f in ff:
        if os.path.basename(f)[:6] == 'sample':
            pass
        else:
            sub(f, yn, mm)
    print()
    
def main():
    proc('N', 'min')
    proc('N', 'max')
    proc('Y', 'max')
    proc('Y', 'min')
    
main()
