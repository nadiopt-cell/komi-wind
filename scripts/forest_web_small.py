import numpy as np, sys
from PIL import Image
sys.path.insert(0,'scripts')
from common import *
a=np.load('build/forest_merc_sm.npy')
h,w=a.shape
small=np.asarray(Image.fromarray(a,'L').resize((3000, int(h*3000/w)), Image.NEAREST))
PAL={1:(58,116,84),3:(74,120,72),4:(214,178,110),5:(142,168,86)}
out=np.zeros((*small.shape,4),dtype='uint8')
for k,c in PAL.items():
    m=small==k; out[m,0]=c[0]; out[m,1]=c[1]; out[m,2]=c[2]; out[m,3]=255
Image.fromarray(out,'RGBA').save('web/data/forest_merc.png')
import os
print(small.shape, round(os.path.getsize('web/data/forest_merc.png')/1e6,2),'MB')
