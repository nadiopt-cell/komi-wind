import numpy as np, rasterio, os, glob, json
from rasterio.transform import from_origin
from rasterio.warp import reproject, Resampling
from rasterio.enums import Resampling as RS
from rasterio.vrt import WarpedVRT
from rasterio.crs import CRS
import sys
sys.path.insert(0,'scripts')
from common import AEA, X0, Y0, X1, Y1, RES, W, H

print('grid', W, H, RES)
dst_crs = CRS.from_user_input(AEA)
transform = from_origin(X0, Y1, RES, RES)

acc = np.zeros((H, W), dtype=np.float64)
cnt = np.zeros((H, W), dtype=np.uint8)
files = sorted(glob.glob(r'C:\grass_tmp\dem\*.tif'))
print('tiles', len(files))
for i,f in enumerate(files):
    try:
        with rasterio.open(f) as src:
            with WarpedVRT(src, crs=dst_crs, transform=transform, width=W, height=H,
                           resampling=Resampling.bilinear, src_nodata=src.nodata,
                           nodata=-9999.0, add_alpha=False) as vrt:
                a = vrt.read(1, masked=True)
                m = (~a.mask) & (a.data > -1000) & (a.data < 9000)
                acc[m] += a.data[m]; cnt[m] += 1
    except Exception as e:
        print('ERR', f, e)
    if i % 40 == 0: print(i, flush=True)
np.save('build/coverage.npy', (cnt>0).astype('uint8'))
dem = np.where(cnt>0, acc/np.maximum(cnt,1), np.nan).astype('float32')
print('elev', np.nanmin(dem), np.nanmax(dem), np.isnan(dem).sum())
# fill nan by nearest
from scipy import ndimage
mask = np.isnan(dem)
if mask.any():
    ind = ndimage.distance_transform_edt(mask, return_distances=False, return_indices=True)
    dem = dem[tuple(ind)]
os.makedirs('build', exist_ok=True)
with rasterio.open('build/dem_aea.tif','w', driver='GTiff', height=H, width=W, count=1,
                   dtype='float32', crs=dst_crs, transform=transform, compress='deflate', tiled=True) as dst:
    dst.write(dem, 1)
print('saved dem')
np.save('build/dem.npy', dem)
