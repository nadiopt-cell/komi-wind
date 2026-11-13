import numpy as np, rasterio, sys
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_bounds
from rasterio.crs import CRS
from PIL import Image
sys.path.insert(0,'scripts')
from common import *

rel = np.asarray(Image.open('build/relief_full.png').convert('RGB')).transpose(2,0,1)
src_crs = CRS.from_user_input(AEA)
src_transform = from_bounds(X0, Y0, X1, Y1, W, H)

# mercator bounds
from pyproj import Transformer
t = Transformer.from_crs(4326, 3857, always_xy=True)
x0, y0 = t.transform(WEB_LON[0], WEB_LAT[0])
x1, y1 = t.transform(WEB_LON[1], WEB_LAT[1])
Wm = WEB_W
Hm = int(round(Wm * (y1-y0)/(x1-x0)))
print('merc', Wm, Hm, x0, y0, x1, y1)
dst_transform = from_bounds(x0, y0, x1, y1, Wm, Hm)
out = np.zeros((3, Hm, Wm), dtype='uint8')
for b in range(3):
    reproject(rel[b].astype('float32'), out[b], src_transform=src_transform, src_crs=src_crs,
              dst_transform=dst_transform, dst_crs='EPSG:3857', resampling=Resampling.bilinear)
img = Image.fromarray(out.transpose(1,2,0))
img.save('web/data/relief_merc.jpg', quality=88, optimize=True)
print('saved', img.size)
import json
json.dump({'bounds':[x0,y0,x1,y1], 'size':[Wm,Hm], 'lonlat':WEB_LON+WEB_LAT}, open('build/web_relief_meta.json','w'))
