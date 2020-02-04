import os
import glob
from fileio import load_core

def load():
    ans = []
    for f in glob.glob('/Github/sensfre/CabinetApproval/data/*.txt'):
        if os.path.basename(f)[:6] == 'sample': continue
        data, names = load_core(f)
        ans.append([list(data[0])[:4], f])
    return ans
    
def main():
    for r, f in sorted(load()):
        d1 = r[0].strftime('%Y-%m-%d')
        d2 = r[1].strftime('%Y-%m-%d')
        print('%s %s %4.1f %4.1f  %s' % (d1, d2, r[2], r[3], f))
    
main()
