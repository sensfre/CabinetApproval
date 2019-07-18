"""fileio.py データファイルの読み込み
"""
from datetime import datetime, timedelta
import numpy as np

# Excel の仕様には、「1900-01-01 を 1 とする連番で日付を表現する」という記述が
# あるが、この連番は 1900 年を閏年として扱うという誤りが存在する。
# つまり、実際には存在しない 1900-02-29 にも連番が割り当てられている。
# 他システムとの整合を取るには 1900-01-01～1900-02-28 は除外した方がよい。
#
__EXCEL_SERIAL_YMD = (1900, 3, 1)
__EXCEL_SERIAL_ORG = 61

def sn_fm_dt(dt):
    """
    Parameters
    ----------
    dt, datetime :
    
    Returns
    ----------
    serial number, float : serial date in Excel (1900-03-01 => 61)
    
    Bugs
    ----
    1900-03-01 以降で有効
    
    """
    s0, d0 = __EXCEL_SERIAL_ORG, datetime(*__EXCEL_SERIAL_YMD)
    delta = dt - d0
    sn = s0 + delta.days + delta.seconds/86400
    return sn
    
    
def dt_fm_sn(sn):
    """
    Parameters
    ----------
    serial number, float : serial date in Excel (1900-03-01 => 61)
    
    Returns
    ----------
    dt, datetime :
    
    Bugs
    ----
    1900-03-01 以降で有効
    
    """
    s0, d0 = __EXCEL_SERIAL_ORG, datetime(*__EXCEL_SERIAL_YMD)
    d, f = divmod(sn - s0, 1)
    return d0 + timedelta(days=int(d), seconds=(f*86400))
    
    
def load_core(fn):
    """
    Parameters
    ----------
    fn, string : 入力ファイル名

    Returns
    -------
    data, structured arrays :
             data[0] は 第 0 行。
             data[0]['DATE1'] は、第 0 行の DATE1 フィールド。
             data['DATE1'] は フィールド名が DATE1 の列。
             data['DATE1'][0] は、DATE1 フィールドの第 0 行。
             (data['DATE1'][0] と data[0]['DATE1'] は等価)
    
    names, list of str. : Notes 参照
    
    Notes
    -----
    先頭が '#' で始まる行はコメント行
    想定するフィールド (names) は以下の通り
          'DATE1'  日付1
          'DATE2'  日付2
          'APP'    Approval Rate (支持率)
          'NAP'    Not Approval Rate (不支持率)
          'N_RES'  Number of Responss (回答数)
          
    ファイルに記述された順番のまま (日付によるソートはしない)。
    日付は serial 値ではなく datetime で保持する
    
    """
    def _dt(x):
        dt = datetime.strptime(x.decode('utf8'), '%Y-%m-%d')
        return dt
        
    _dtype = (datetime, datetime, float, float, float)
    data = np.genfromtxt(fn,
                names=True,
                dtype = _dtype,
                converters={0:_dt, 1:_dt},
                usecols=range(len(_dtype)),
    )
    return data, data.dtype.names
    
    
