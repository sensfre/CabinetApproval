import os
import argparse
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

cfg = {
    'gout_date': datetime.now().strftime('%Y%m%d'), # file 名に日付を付加する
    'args': None,    # parse_args() の戻り値を保持する
}

def options():
    """ オプション定義
    Returns
    -------
    opt : ArgumentParser() インスタンス
    
    """
    opt = argparse.ArgumentParser(description='Twitter プロファイル画像編集')
    
    # GOUT
    opt.add_argument('-f', dest='gout_folder', default='../output',
                help='グラフの出力先フォルダ (../output)')
    
    return opt
    
    
def main():
    opt = options()
    cfg['args'] = opt.parse_args()
    args = cfg['args']
    
    # 新しい画像を用意して、背景を白に設定する
    #
    im_base = Image.new("RGB", (1500, 500))
    draw = ImageDraw.Draw(im_base)
    draw.rectangle((0,0,1500,500), fill=(255,255,255))
    
    # サマリーをコピペ
    #
    im_summary = Image.open(os.path.join(args.gout_folder, 'Fig1_%s.png' % cfg['gout_date']))
    im_base.paste(im_summary, (850, 0))
    
    x_last = 460
    
    # 最新動向をコピペ(縮小)
    #
    im_last = Image.open(os.path.join(args.gout_folder, 'Fig10_%s.png' % cfg['gout_date']))
    im = im_last.crop((40+105, 0, 482+105, 472))   # (442 x 472) 
    im = im.resize((int(442*0.95), int(472*0.95)), resample=Image.BILINEAR)
    im_base.paste(im, (x_last, 0))
    
    # 最新動向の凡例をコピペ
    #
    im = im_last.crop((585, 53, 700+5, 297))
    # im_base.paste(im, (x_last - 120, 47+8))
    im_base.paste(im, (x_last - 120, 47-15))
    
    # 透過属性ありの draw を使って グループ H/L をハッチング
    #
    draw = ImageDraw.Draw(im_base, 'RGBA')
    font = ImageFont.truetype("c:/Windows/Fonts/meiryob.ttc", 12)
    font2 = ImageFont.truetype("c:/Windows/Fonts/meiryob.ttc", 20)
    
    # グループ H のハッチング
    #
    (x1, y1), (x2, y2) = (x_last - 190, 80-22), (x_last - 4 + 5, 146)
    draw.polygon([(x1, y1), (x1, y2), (x2, y2), (x2, y1)], (128, 0, 255, 32))
    draw.text((x1+6, y1+6), 'グループ H', fill=(0,0,0), font=font)
    
    # グループ L のハッチング
    #
    (x1, y1), (x2, y2) = (x_last - 190, 146), (x_last - 4 + 5, 260 - 20)
    draw.polygon([(x1, y1), (x1, y2), (x2, y2), (x2, y1)], (0, 128, 64, 32))
    draw.text((x1+6, y1+6), 'グループ L', fill=(0,0,0), font=font)
    
    # アイキャッチ
    if 1:
        x1, y1 = 10, 30
        #draw.text((x1, y1+  0), '報道各社の内閣支持率は、', fill=(0,0,0), font=font2)
        #draw.text((x1, y1+ 30), 'バラバラだけど...', fill=(0,0,0), font=font2)
        #draw.text((x1, y1+ 60), 'デタラメじゃない!', fill=(0,0,0), font=font2)
        #draw.text((x1, y1+ 100), '傾向はとても安定してる。', fill=(0,0,0), font=font2)
    
    # 保存
    #
    im_base.save(os.path.join(args.gout_folder, 'FigH_%s.png' % cfg['gout_date']))
    
    
if __name__ == '__main__':
    main()
    
    
