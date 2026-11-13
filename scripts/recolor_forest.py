import numpy as np, sys
from PIL import Image
sys.path.insert(0,'scripts')
from common import *
PAL = {1:(58,116,84), 3:(74,120,72), 4:(214,178,110), 5:(142,168,86)}
def colorize(arr, path, alpha=255):
    h,w = arr.shape
    out = np.zeros((h,w,4), dtype='uint8')
    for k,c in PAL.items():
        m = arr==k
        out[m,0]=c[0]; out[m,1]=c[1]; out[m,2]=c[2]; out[m,3]=alpha
    Image.fromarray(out,'RGBA').save(path)
colorize(np.load('build/forest_aea_sm.npy'), 'build/forest_aea.png')
colorize(np.load('build/forest_merc_sm.npy'), 'web/data/forest_merc.png')
print('done')
