import qrcode
import os
import pandas as pd
import numpy as np
import argparse
import hashlib
import time
import cv2
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


args = argparse.ArgumentParser()
args.add_argument('--input', type=str, default='input.csv')
args.add_argument('--template', type=str, default='badge_template.png')
args.add_argument('--output_dir', type=str, default='output')
args.add_argument('--output_file', type=str, default='output.csv')

args = args.parse_args()

if not os.path.exists(args.output_dir):
    os.mkdir(args.output_dir)

out_df = pd.DataFrame(columns=['name', 'surname', 'code'])
df = pd.read_csv(args.input)


def read_badge_template():
    img = Image.open(args.template)
    # img = img.resize((img.size[0]*2, img.size[1]*2))
    return img


def draw_text(img, text, x, y, font, color):
    draw = ImageDraw.Draw(img)
    _, _, w, h = draw.textbbox((0, 0), text, font=font)
    draw.text((x-(w/2), y-(h/2)), text, color, font=font)
    return img


def generate_qr_code(name, surname):
    hash = hashlib.sha256()
    hash.update(name.encode('utf-8'))
    hash.update(surname.encode('utf-8'))
    hash.update(str(time.time()).encode('utf-8'))
    hash = hash.hexdigest()
    img = qrcode.make(hash[:16])
    img = img.resize((120, 120))
    return img, hash


def add_qr_code(img, qr_code, x, y):
    print(qr_code)
    w, h = qr_code.size
    img.paste(qr_code, (x-(w//2), y-(h//2)))
    return img


for i, row in df.iterrows():
    flg = 0
    if i % 4 == 0:
        badge_img = read_badge_template()

    w, h = badge_img.size

    if i % 4 == 0:
        ref_x = w//4
        ref_y = h//4
    elif i % 4 == 1:
        ref_x = w//4
        ref_y = h//4*3
    elif i % 4 == 2:
        ref_x = w//4*3
        ref_y = h//4
    elif i % 4 == 3:
        ref_x = w//4*3
        ref_y = h//4*3

    badge_img = draw_text(badge_img, row['name'], ref_x, ref_y -80, ImageFont.truetype('/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf', 28), (0, 0, 0))
    badge_img = draw_text(badge_img, row['pos'], ref_x, ref_y -50, ImageFont.truetype('/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf', 24), (0, 0, 0))
    badge_img = draw_text(badge_img, row['affiliation'], ref_x, ref_y -10, ImageFont.truetype('/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf', 20), (0, 0, 0))
    qrcode_img, hash = generate_qr_code(row['name'], row['affiliation'])
    final_img = add_qr_code(badge_img, qrcode_img, ref_x, ref_y+80)

    out_df = out_df.append({'name': row['name'], 'surname': row['affiliation'], 'code': hash}, ignore_index=True)

    #
    #

    if i % 4 == 3:
        final_img.show()
        flg = 1
    # # img.save(os.path.join(args.output_dir, hash + '.png'))
if flg == 0:
    final_img.show()


# out_df.to_csv(args.output_file, index=False)


