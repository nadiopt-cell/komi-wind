import numpy as np, sys
from scipy import ndimage
from PIL import Image
sys.path.insert(0,'scripts')
from common import *

def majority(arr, size=5):
    classes = [0,1,3,4,5,255]
    stack = []
    for k in classes:
        m = (arr==k).astype('float32')
        stack.append(ndimage.uniform_filter(m, size=size, mode='nearest'))
    st = np.stack(stack, 0)
    idx = np.argmax(st, 0)
    out = np.array(classes, dtype='uint8')[idx]
    return out

for name, path in [('aea','build/forest_aea.npy'), ('merc','build/forest_merc.npy')]:
    a = np.load(path)
    b = majority(a, 5 if name=='aea' else 5)
    np.save(path.replace('.npy','_sm.npy'), b)
    print(name, np.unique(b, return_counts=True))

PAL = {1:(47,107,79), 3:(63,110,62), 4:(198,161,91), 5:(126,154,78)}
def colorize(arr, path):
    h,w = arr.shape
    out = np.zeros((h,w,4), dtype='uint8')
    for k,c in PAL.items():
        m = arr==k
        out[m,0]=c[0]; out[m,1]=c[1]; out[m,2]=c[2]; out[m,3]=255
    Image.fromarray(out,'RGBA').save(path)
    return out
o1 = colorize(np.load('build/forest_aea_sm.npy'), 'build/forest_aea.png')
o2 = colorize(np.load('build/forest_merc_sm.npy'), 'web/data/forest_merc.png')
Image.fromarray(o1).resize((1000,1000), Image.LANCZOS).save('build/preview_forest.png')

# composite preview
rel = np.asarray(Image.open('build/relief_full.png').convert('RGB')).astype('float32')
al = 0.45
rgb = rel*(1-al) + o1[...,:3].astype('float32')*al
Image.fromarray(rgb.astype('uint8')).resize((1100,1100), Image.LANCZOS).save('build/preview_forest_comp.png')
print('ok')
