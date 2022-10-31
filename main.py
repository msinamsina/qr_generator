import qrcode
import os
import pandas as pd
import numpy as np
import argparse
import hashlib
import time
from PIL import Image

args = argparse.ArgumentParser()
args.add_argument('--input', type=str, default='input.csv')
args.add_argument('--output_dir', type=str, default='output')
args.add_argument('--output_file', type=str, default='output.csv')

args = args.parse_args()

if not os.path.exists(args.output_dir):
    os.mkdir(args.output_dir)

out_df = pd.DataFrame(columns=['name', 'surname', 'code'])
df = pd.read_csv(args.input)

for i, row in df.iterrows():
    hash = hashlib.sha256()
    hash.update(row['name'].encode('utf-8'))
    hash.update(row['surname'].encode('utf-8'))
    hash.update(str(time.time()).encode('utf-8'))
    hash = hash.hexdigest()
    print(hash)
    img = qrcode.make(hash)
    img.save(os.path.join(args.output_dir, hash + '.png'))
    out_df = out_df.append({'name': row['name'], 'surname': row['surname'], 'code': hash}, ignore_index=True)

out_df.to_csv(args.output_file, index=False)


