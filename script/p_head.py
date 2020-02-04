import glob
import time

def load():
    def _rec(fn):
        f = open(fn)
        while 1:
            xx = f.readline() # skip header
            x = xx.strip().split()
            if xx[0] == '#': continue
            if (x[0].strip())[:4] == 'DATE': continue
            break
        f.close()
        return xx.strip().split()
        
    ff = glob.glob('/Github/sensfre/CabinetApproval/data/*.txt')
    rr = [_rec(f) for f in ff]
    d1 = [time.strptime(a[0], '%Y-%m-%d') for a in rr]
    d2 = [time.strptime(a[1], '%Y-%m-%d') for a in rr]
    return zip(d1, d2, rr, ff)
    
def main():
    for d1, d2, r, f in sorted(load()):
        print('%s %s %4.1f %4.1f  %s' % (r[0], r[1], float(r[2]), float(r[3]), f))
    
main()
