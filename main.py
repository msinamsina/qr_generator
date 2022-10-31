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
import arabic_reshaper
from bidi.algorithm import get_display



args = argparse.ArgumentParser()
args.add_argument('--input', type=str, default='input.xlsx')
args.add_argument('--template', type=str, default='badge_template.png')
args.add_argument('--output_dir', type=str, default='output')
args.add_argument('--output_file', type=str, default='output.csv')

args = args.parse_args()

if not os.path.exists(args.output_dir):
    os.mkdir(args.output_dir)

out_df = pd.DataFrame(columns=['name', 'surname', 'code'])
df = pd.read_excel(args.input)


def read_badge_template(path):
    img = Image.open(path)
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
    hash = name+surname+hash.hexdigest()[:5]
    img = qrcode.make(hash)
    img = img.resize((140, 140))
    return img, hash


def add_qr_code(img, qr_code, x, y):
    print(qr_code)
    w, h = qr_code.size
    img.paste(qr_code, (x-(w//2), y-(h//2)))
    return img


for i, row in df.iterrows():
    print(row['Badge Type'])
    badge_img = read_badge_template(row['Badge Type']+'.PNG')

    w, h = badge_img.size
    ref_x = w//2
    ref_y = h//2

    badge_img = draw_text(badge_img, get_display(arabic_reshaper.reshape(str(row['Name']))), ref_x, ref_y -80, ImageFont.truetype('times.ttf', 20), (0, 0, 0))
    badge_img = draw_text(badge_img, get_display(arabic_reshaper.reshape(str(row['Position']))), ref_x, ref_y -50, ImageFont.truetype('times.ttf', 18), (0, 0, 0))
    badge_img = draw_text(badge_img, get_display(arabic_reshaper.reshape(str(row['Affiliation']))), ref_x, ref_y -10, ImageFont.truetype('times.ttf', 17), (0, 0, 0))
    qrcode_img, hash = generate_qr_code(str(row['Name']), str(row['Affiliation']))
    final_img = add_qr_code(badge_img, qrcode_img, ref_x, ref_y+80)

    out_df = out_df.append({'name': row['Name'], 'surname': row['Affiliation'], 'code': hash}, ignore_index=True)
    # final_img.show()
    final_img.save(os.path.join(args.output_dir, hash + '.png'))

out_df.to_csv(args.output_file, index=False)


