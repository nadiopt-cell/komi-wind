from PIL import Image
frames=[Image.open(f'build/gif_{i}.png').convert('RGB') for i in range(1,7)]
w,h=frames[0].size
scale=1200/w
g=[f.resize((1200,int(h*scale)), Image.LANCZOS) for f in frames]
pal=[f.quantize(colors=256, method=Image.MEDIANCUT, dither=Image.FLOYDSTEINBERG) for f in g]
pal[0].save('output/interactions_komi.gif', save_all=True, append_images=pal[1:],
            duration=[1300,1300,1300,1300,1600,3200], loop=0, optimize=True, disposal=2)
import os
print('gif bytes', os.path.getsize('output/interactions_komi.gif')/1e6, 'MB', g[0].size)
