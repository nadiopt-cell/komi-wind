import numpy as np, sys, os
sys.path.insert(0,'scripts')
from common import *
from PIL import Image

dem0 = np.load('build/dem.npy').astype('float32')
PAD = 90
dem = np.pad(dem0, PAD, mode='edge')
H_, W_ = dem0.shape
res = RES

def hs(az_deg, alt_deg=40.0, z=1.15):
    az = np.deg2rad(az_deg); alt = np.deg2rad(alt_deg)
    gy, gx = np.gradient(dem * z, res)
    slope = np.arctan(np.hypot(gx, gy))
    aspect = np.arctan2(-gx, gy)
    aspect = np.where(aspect < 0, 2*np.pi + aspect, aspect)
    s = np.sin(alt)*np.cos(slope) + np.cos(alt)*np.sin(slope)*np.cos(az - aspect)
    return np.clip(s, 0, 1)

shade = (0.46*hs(315) + 0.22*hs(345) + 0.17*hs(285) + 0.15*hs(200))
p2, p98 = np.percentile(shade, [1, 99])
shade = np.clip((shade - p2)/(p98-p2), 0, 1)
shade = shade**0.95
shade = shade[PAD:-PAD, PAD:-PAD]
print('shade', np.percentile(shade,[1,50,99]))

stops = [(0,(241,235,223)),(150,(234,226,211)),(300,(226,216,198)),(500,(215,202,184)),
         (800,(202,188,169)),(1100,(188,173,155)),(1500,(172,157,141)),(1900,(157,143,130))]
e = np.clip(dem0, 0, 1900)
rgb = np.zeros((H_,W_,3), dtype='float32')
for i in range(len(stops)-1):
    e0,c0 = stops[i]; e1,c1 = stops[i+1]
    m = (e>=e0)&(e<e1)
    t = (e[m]-e0)/(e1-e0)
    for k in range(3):
        rgb[m,k] = c0[k] + t*(c1[k]-c0[k])
m = e>=stops[-1][0]
rgb[m] = stops[-1][1]

sh = shade[...,None]
out = rgb * (0.52 + 0.62*sh)
out = np.clip(out, 0, 255)
cov = np.load('build/coverage.npy').astype('float32')
from scipy import ndimage as ndi
cov = ndi.uniform_filter(cov, 9)
paper = np.array([246,242,234], dtype='float32')
out = out*cov[...,None] + paper*(1-cov[...,None])
img = Image.fromarray(out.astype('uint8'))
img.save('build/relief_full.png')
np.save('build/shade.npy', shade.astype('float32'))
img.resize((1200,1200), Image.LANCZOS).save('build/preview_relief.png')
print('ok')
