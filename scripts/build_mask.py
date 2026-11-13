import numpy as np, geopandas as gpd, rasterio, sys
from rasterio.features import rasterize
from rasterio.transform import from_origin
sys.path.insert(0,'scripts')
from common import *
from PIL import Image

komi = gpd.read_file('web/data/komi.geojson').to_crs(AEA)
tr = from_origin(X0, Y1, RES, RES)
mask = rasterize([(g,1) for g in komi.geometry], out_shape=(H,W), transform=tr, fill=0, dtype='uint8')
np.save('build/komi_mask.npy', mask)
print('inside frac', mask.mean())

# ghost outside komi
rel = np.asarray(Image.open('build/relief_full.png').convert('RGB')).astype('float32')
paper = np.array([246,242,234], dtype='float32')
a = (mask.astype('float32')*0.65 + 0.35)[...,None]
out = rel*a + paper*(1-a)
Image.fromarray(np.clip(out,0,255).astype('uint8')).save('build/relief_poster.png')
Image.fromarray(np.clip(out,0,255).astype('uint8')).resize((1200,1200), Image.LANCZOS).save('build/preview_relief2.png')
