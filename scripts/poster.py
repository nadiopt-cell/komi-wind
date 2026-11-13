# -*- coding: utf-8 -*-
import numpy as np, geopandas as gpd, sys, os, math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection, LineCollection
from matplotlib import colors as mcolors
from matplotlib.patches import Rectangle, FancyArrowPatch
from matplotlib.lines import Line2D
from matplotlib import patheffects as pe
from PIL import Image
from pyproj import Transformer
sys.path.insert(0,'scripts')
from common import *

komi = gpd.read_file('web/data/komi.geojson').to_crs(AEA)
oopt = gpd.read_file('web/data/oopt.geojson').to_crs(AEA)
wf   = gpd.read_file('web/data/windfalls.geojson').to_crs(AEA)
arr  = gpd.read_file('web/data/arrows.geojson').to_crs(AEA)
heads= gpd.read_file('web/data/arrowheads.geojson').to_crs(AEA)
rv   = gpd.read_file('build/rivers_osm.gpkg').to_crs(AEA)
lk   = gpd.read_file('build/lakes_osm.gpkg').to_crs(AEA)
ne   = gpd.read_file('web/data/rivers.geojson').to_crs(AEA)

def polys_of(gdf):
    out=[]
    for g in gdf.geometry:
        if g is None or g.is_empty: continue
        if g.geom_type=='Polygon': out.append(g)
        elif g.geom_type=='MultiPolygon': out.extend(g.geoms)
    return out

LK_V  = [np.asarray(p.exterior.coords) for p in polys_of(lk)]
OOPS_V= [np.asarray(p.exterior.coords) for p in polys_of(oopt)]
WCOL  = [mcolors.to_rgba(c) for c in RAMP]
WP=[]; WC=[]
for g, per in zip(wf.geometry, wf['period']):
    i = PERIODS.index(per) if per in PERIODS else 0
    if g.geom_type=='Polygon': WP.append(g); WC.append(WCOL[i])
    elif g.geom_type=='MultiPolygon':
        for p in g.geoms: WP.append(p); WC.append(WCOL[i])
WP_V = [np.asarray(p.exterior.coords) for p in WP]
AR_SEGS = [np.asarray(g.coords) for g in arr.geometry]
AR_COL = [WCOL[PERIODS.index(p)] if p in PERIODS else (1,1,1,1) for p in arr['period']]
RIV = {0.42:[], 0.6:[], 0.8:[]}
for g, wv in zip(rv.geometry, rv['width']):
    if g.geom_type=='LineString': RIV[wv].append(np.asarray(g.coords))
    elif g.geom_type=='MultiLineString': RIV[wv].extend([np.asarray(p.coords) for p in g.geoms])
KOMI_RINGS=[]
kg = komi.geometry.iloc[0]
for g in (kg.geoms if hasattr(kg,'geoms') else [kg]):
    KOMI_RINGS.append(np.asarray(g.exterior.coords))
    KOMI_RINGS.extend([np.asarray(r.coords) for r in g.interiors])

AR_HCOL = [WCOL[PERIODS.index(p)] if p in PERIODS else (1,1,1,1) for p in heads['period']]

def arrow_tris(heads, L=2400, Wd=1050):
    tris=[]
    for g,b in zip(heads.geometry, heads['bearing']):
        x,y=g.x,g.y; th=np.deg2rad(b)
        ux,uy=np.sin(th),np.cos(th); vx,vy=np.cos(th),-np.sin(th)
        tris.append([(x-ux*L+vx*Wd/2,y-uy*L+vy*Wd/2),(x,y),(x-ux*L-vx*Wd/2,y-uy*L-vy*Wd/2)])
    return tris
TRI = arrow_tris(heads)

REL = np.asarray(Image.open('build/relief_full.png').convert('RGB'))
FOR = np.asarray(Image.open('build/forest_aea.png').convert('RGBA'))
EX0, EY0, EX1, EY1 = -486000.0, -462000.0, 496000.0, 306000.0

def draw_map(ax, extent, detail=False):
    ax.set_xlim(extent[0], extent[2]); ax.set_ylim(extent[1], extent[3])
    ax.set_aspect('equal'); ax.axis('off')
    ax.imshow(REL, extent=(X0,X1,Y0,Y1), origin='upper', zorder=0, interpolation='lanczos')
    ax.imshow(FOR, extent=(X0,X1,Y0,Y1), origin='upper', zorder=1, interpolation='lanczos', alpha=(0.55 if detail else 0.42))
    ax.add_collection(PolyCollection(LK_V, facecolors='#BBD0D9', edgecolors='#8FB0BE', linewidths=0.3, zorder=2, alpha=0.9))
    for wv,lw,al,col in [(0.42,0.28,0.32,'#7FA0B2'),(0.6,0.5,0.48,'#6B93A8'),(0.8,0.95,0.78,'#577F97')]:
        if RIV[wv]:
            ax.add_collection(LineCollection(RIV[wv], colors=col, linewidths=lw*(2.0 if detail else 1.0), alpha=al, zorder=2.5, capstyle='round'))
    ax.add_collection(PolyCollection(OOPS_V, facecolors='#2F6F6B', edgecolors='none', alpha=0.13, zorder=3))
    ax.add_collection(PolyCollection(OOPS_V, facecolors='none', edgecolors='#14514E', linewidths=(1.3 if detail else 0.7), alpha=0.95, linestyles=(0,(3,2)), zorder=3.1))
    # halo + fill for windfalls
    ax.add_collection(PolyCollection(WP_V, facecolors='none', edgecolors='#FBF8F2', linewidths=(1.8 if detail else 1.1), alpha=0.55, zorder=3.9))
    ax.add_collection(PolyCollection(WP_V, facecolors=WC, edgecolors='#3B1027', linewidths=(0.8 if detail else 0.38), alpha=0.97, zorder=4))
    ax.add_collection(LineCollection(AR_SEGS, colors='#241F1A', linewidths=(4.4 if detail else 2.7), alpha=(0.42 if detail else 0.34), zorder=5, capstyle='round'))
    ax.add_collection(LineCollection(AR_SEGS, colors=AR_COL, linewidths=(2.1 if detail else 1.35), alpha=1.0, zorder=5.1, capstyle='round'))
    ax.add_collection(PolyCollection(TRI, facecolors=AR_HCOL, edgecolors='#241F1A', linewidths=(1.3 if detail else 0.85), zorder=5.3))
    ax.add_collection(LineCollection(KOMI_RINGS, colors='#241F1A', linewidths=(2.6 if detail else 1.55), alpha=0.9, zorder=6))

W_PX, H_PX, DPI = 4200, 5400, 200
fig = plt.figure(figsize=(W_PX/DPI, H_PX/DPI), dpi=DPI)
fig.patch.set_facecolor('#FBF8F2')
SERIF='Georgia'; SANS='Segoe UI'
INK='#241F1A'; MUTED='#6F655A'; RULE='#C9BFB0'; SUBT='#8A7F71'; MAG='#7A1C78'
def fx(px): return px/W_PX
def fy(px): return 1-px/H_PX
def fp(size, family=SANS, weight='normal', color=INK, style='normal'):
    return dict(family=family, fontsize=size, fontweight=weight, color=color, fontstyle=style)
def halo(w=4, c='#FBF8F2'): return [pe.withStroke(linewidth=w, foreground=c)]

# ================= HEADER =================
fig.text(fx(220), fy(96), '30DAYMAPCHALLENGE 2026   ·   DAY 13   ·   INTERACTIONS',
         **fp(24, SANS, 'bold', SUBT), ha='left', va='center')
fig.text(fx(214), fy(252), 'Ветер × рельеф × лес',
         **fp(102, SERIF, 'bold', INK), ha='left', va='center')
fig.text(fx(220), fy(465), 'Республика Коми · ветровалы 1984–2026 в рельефе, лесах и на охраняемых территориях',
         **fp(30, SANS, 'normal', MUTED), ha='left', va='center')
fig.add_artist(Line2D([fx(220), fx(3980)], [fy(515), fy(515)], color=RULE, lw=1.6))

# header right note

# ================= MAIN MAP =================
ax = fig.add_axes([fx(220), fy(3491), 3760/W_PX, 2941/H_PX])
draw_map(ax, (EX0, EY0, EX1, EY1))

sb_x, sb_y = EX1-390000, EY0+35000
ax.plot([sb_x, sb_x+100000],[sb_y, sb_y], color=INK, lw=5, solid_capstyle='butt', zorder=8)
ax.plot([sb_x, sb_x],[sb_y-6000, sb_y+6000], color=INK, lw=3, zorder=8)
ax.plot([sb_x+100000, sb_x+100000],[sb_y-6000, sb_y+6000], color=INK, lw=3, zorder=8)
ax.text(sb_x+50000, sb_y+12000, '100 км', ha='center', va='bottom', **fp(23, SANS, 'bold', INK), zorder=8, path_effects=halo(4))

nx, ny = EX1-55000, EY1-120000
ax.annotate('', xy=(nx, ny+34000), xytext=(nx, ny), arrowprops=dict(arrowstyle='-|>,head_width=0.5,head_length=0.8', color=INK, lw=2.6), zorder=8)
ax.text(nx, ny+42000, 'С', ha='center', va='bottom', **fp(25, SANS, 'bold', INK), zorder=8, path_effects=halo(3))

cities = [
 ('Сыктывкар', 50.836, 61.668, 11, -10, 'right'),
 ('Ухта', 53.684, 63.567, 9, 3, 'left'),
 ('Печора', 57.224, 65.145, 9, 2, 'left'),
 ('Вуктыл', 57.316, 63.857, 9, 2, 'left'),
 ('Инта', 60.132, 66.040, 9, 2, 'left'),
 ('Усть-Кулом', 53.687, 61.689, 9, 2, 'left'),
 ('Троицко-Печорск', 56.190, 62.716, 9, 8, 'left'),
 ('Усть-Цильма', 52.193, 65.438, 9, 2, 'left'),
 ('Объячево', 49.633, 60.333, -11, 10, 'right'),
 ('Емва', 50.858, 62.589, -9, 2, 'right'),
]
t = Transformer.from_crs(4326, AEA, always_xy=True)
for name, lon, lat, dx, dy, ha in cities:
    x,y = t.transform(lon, lat)
    if not (EX0 < x < EX1 and EY0 < y < EY1): continue
    ax.plot([x],[y], marker='o', ms=5, mfc='#FBF8F2', mec=INK, mew=1.9, zorder=9)
    ax.annotate(name, xy=(x,y), xytext=(dx,dy), textcoords='offset points', ha=ha, va='center',
                **fp(20, SANS, 'semibold', INK), zorder=9, path_effects=halo(3.4))

def longest_line(g):
    if g.geom_type=='LineString': return g
    if g.geom_type=='MultiLineString': return max(g.geoms, key=lambda x: x.length)
    return None
for _, row in ne.iterrows():
    g = longest_line(row.geometry)
    if g is None or g.length < 20000: continue
    p = g.interpolate(0.5, normalized=True)
    p0 = g.interpolate(0.46, normalized=True); p1 = g.interpolate(0.54, normalized=True)
    ang = math.degrees(math.atan2(p1.y-p0.y, p1.x-p0.x))
    if ang > 90: ang -= 180
    if ang < -90: ang += 180
    if not (EX0 < p.x < EX1 and EY0+20000 < p.y < EY1-20000): continue
    ax.text(p.x, p.y, row['name_ru'], rotation=ang, rotation_mode='anchor', ha='center', va='center',
            **fp(21, SERIF, 'normal', '#2F566B', 'italic'), zorder=8, path_effects=halo(4, '#EFE9DC'))

for nm, lon, lat in [('Печоро-Илычский заповедник', 58.60, 62.15), ('Югыд Ва', 59.45, 64.15)]:
    x,y = t.transform(lon, lat)
    ax.text(x, y, nm, ha='center', va='center', **fp(19, SANS, 'semibold', '#14514E'), zorder=8, path_effects=halo(4))

DCX, DCY, DH = 163955, -136267, 70000
ax.add_patch(Rectangle((DCX-DH, DCY-DH), 2*DH, 2*DH, fill=False, ec=INK, lw=2.0, ls=(0,(7,4)), zorder=10))
ax.text(DCX-DH, DCY-DH-10000, 'см. деталь ↓', ha='left', va='top', **fp(19, SANS, 'semibold', INK), zorder=10, path_effects=halo(4))


# ================= INSET (whole republic) =================
kax = fig.add_axes([fx(258), fy(1035), 430/W_PX, 430/H_PX])
kax.set_facecolor('#FBF8F2')
kax.patch.set_alpha(0.93)
kax.set_xticks([]); kax.set_yticks([])
kb = komi.total_bounds
kx0,kx1 = kb[0]-35000, kb[2]+35000
ky0,ky1 = kb[1]-35000, kb[3]+35000
kax.set_xlim(kx0,kx1); kax.set_ylim(ky0,ky1); kax.set_aspect('equal')
kax.add_collection(LineCollection(KOMI_RINGS, colors='#241F1A', linewidths=1.3, alpha=0.95, zorder=3))
kdots_x=[g.centroid.x for g in wf.geometry]; kdots_y=[g.centroid.y for g in wf.geometry]
kax.plot(kdots_x, kdots_y, ',', color='#7A1C78', ms=1.2, alpha=0.9, zorder=4)
kax.add_patch(Rectangle((EX0,EY0), EX1-EX0, EY1-EY0, fill=False, ec='#7A1C78', lw=1.6, zorder=5))
for sp in kax.spines.values():
    sp.set_visible(True); sp.set_color('#B9AE9C'); sp.set_linewidth(1.2)
fig.text(fx(688), fy(574), 'РЕСПУБЛИКА КОМИ',
         **fp(10.5, SANS, 'bold', '#6F655A'), ha='right', va='bottom',
         bbox=dict(facecolor='#FBF8F2', edgecolor='#B9AE9C', linewidth=0.8, pad=4))
fig.text(fx(688), fy(598), 'рамка — основная карта',
         **fp(9, SANS, 'normal', '#8A7F71'), ha='right', va='bottom',
         bbox=dict(facecolor='#FBF8F2', edgecolor='none', pad=3))

# ================= DETAIL =================
axd = fig.add_axes([fx(220), fy(4800), 1250/W_PX, 1250/H_PX])
draw_map(axd, (DCX-DH, DCY-DH, DCX+DH, DCY+DH), detail=True)
for s in axd.spines.values():
    s.set_visible(True); s.set_color(INK); s.set_linewidth(1.8)
fig.text(fx(220), fy(4850), 'ДЕТАЛЬ · 140 × 140 км', **fp(22, SANS, 'bold', INK), va='top')
fig.text(fx(220), fy(4895), 'Печоро-Илычский заповедник и Илычский\nзаказник: два крупнейших ветровала 1992\nи 2009 гг. и цепочка смерчей 1993 г. на\nзападном склоне Урала. Стрелки показывают,\nоткуда пришёл ветер.',
         **fp(19, SANS, 'normal', MUTED), va='top', linespacing=1.45)

# ================= LEGEND (figure coords) =================
LX = 1560
def ltext(x, y, s, size=20, fam=SANS, weight='normal', color=INK, va='center', ha='left'):
    fig.text(fx(x), fy(y), s, **fp(size, fam, weight, color), va=va, ha=ha)
def lrect(x, y, w, h, fc, ec='none', lw=0.8, alpha=1.0, ls='solid'):
    fig.add_artist(Rectangle((fx(x), fy(y+h)), w/W_PX, h/H_PX, transform=fig.transFigure,
                             fc=fc, ec=ec, lw=lw, alpha=alpha, ls=ls, zorder=5))
def lhead(y, title):
    ltext(LX, y, title, 19, SANS, 'bold', SUBT)

y = 3555
lhead(y, 'ЛЕГЕНДА'); y += 65
crop = REL[2600:2900, 3200:3800]
axr = fig.add_axes([fx(1560), fy(y+66), 130/W_PX, 66/H_PX]); axr.imshow(crop); axr.axis('off')
for sp in axr.spines.values(): sp.set_visible(True); sp.set_color('#B9AE9C'); sp.set_linewidth(0.8)
ltext(1710, y+20, 'Рельеф', 20, SANS, 'semibold')
ltext(1710, y+84, 'Copernicus DEM GLO-90 · отмывка', 15.5, SANS, 'normal', MUTED)
y += 150

lhead(y, 'ПОРОДНЫЙ СОСТАВ ЛЕСА'); y += 62
for c,lab in [('#3A7454','хвойные'), ('#8EA856','смешанные'), ('#D6B26E','лиственные')]:
    lrect(1560, y-14, 68, 28, c, alpha=0.9)
    ltext(1650, y, lab, 20); y += 58
ltext(1650, y-10, 'Copernicus Forest Type · 2019 · 100 м', 16, SANS, 'normal', MUTED); y += 70

lhead(y, 'ОХРАНЯЕМЫЕ ТЕРРИТОРИИ'); y += 62
lrect(1560, y-14, 68, 28, '#2F6F6B', '#14514E', 1.4, 0.30, (0,(2.5,1.6)))
ltext(1650, y, 'ООПТ · 282 контура', 20); y += 85

lhead(y, 'ГИДРОГРАФИЯ'); y += 62
fig.add_artist(Line2D([fx(1560), fx(1628)], [fy(y), fy(y)], color='#577F97', lw=1.8))
ltext(1650, y, 'реки и озёра · OSM', 20); y += 85

lhead(y, 'ВЕТРОВАЛЫ · 5-ЛЕТНИЕ ПЕРИОДЫ'); y += 62
cnt = wf.groupby('period').size().to_dict()
for i,(per,col) in enumerate(zip(PERIODS, RAMP)):
    colx = LX if i < 5 else LX+480
    yy = y + (i%5)*58
    lrect(colx, yy-14, 62, 28, col, '#3B1027', 0.7)
    ltext(colx+76, yy, ('2025 →' if per=='2025–2029' else per), 17)
    ltext(colx+400, yy, f'{cnt.get(per,0)}', 17, SANS, 'semibold', MUTED, ha='right')
y += 5*58 + 35

lhead(y, 'НАПРАВЛЕНИЕ ВЕТРА'); y += 60
fig.add_artist(FancyArrowPatch((fx(1560), fy(y+30)), (fx(1650), fy(y-8)),
    arrowstyle='-|>,head_width=0.35,head_length=0.7', color='#A02C7C', lw=2.0, transform=fig.transFigure, zorder=6,
    shrinkA=0, shrinkB=0))
ltext(1670, y-4, 'начало — откуда пришёл шквал', 17)
ltext(1670, y+28, 'острие — куда он ударил', 17)

# ================= STATS =================
SX = 2870
def stext(x, y, s, size=20, fam=SANS, weight='normal', color=INK, va='center', ha='left', linespacing=1.2):
    fig.text(fx(x), fy(y), s, **fp(size, fam, weight, color), va=va, ha=ha, linespacing=linespacing)
stext(SX, 3565, 'ВЗАИМОДЕЙСТВИЕ В ЦИФРАХ', 19, SANS, 'bold', SUBT)
stats = [('401','ветровал · 1984–2026'), ('53 279','га суммарной площади'),
         ('20 %','площади — в границах ООПТ'), ('67 %','событий — с запада и юго-запада')]
yy = 3650
for big, cap in stats:
    stext(SX, yy, big, 50, SERIF, 'bold', va='top')
    stext(SX, yy+146, cap, 18.5, SANS, 'normal', MUTED, va='top')
    yy += 222
fig.add_artist(Line2D([fx(SX), fx(3980)], [fy(yy+18), fy(yy+18)], color=RULE, lw=1.2))
stext(SX, yy+45,
 'Шквалы и смерчи приходят с запада и юго-запада,\n'
 'пересекают Вычегду и Сысолу и упираются\n'
 'в западный склон Урала. Больше всего леса\n'
 'гибнет в полосе 100–250 м — в темнохвойной\n'
 'тайге на выровненных междуречьях;\n'
 'на подъёме к Уралу ветровалы редеют.\n'
 'Каждый пятый гектар поваленного леса —\n'
 'в ООПТ: крупнейшие события 1992 и 2009 гг.\n'
 'пришлись на Печоро-Илычский заповедник\n'
 'и Илычский заказник.',
 16.5, SANS, 'normal', '#3A332C', va='top', linespacing=1.42)

# ================= FOOTER =================
fig.add_artist(Line2D([fx(220), fx(3980)], [fy(5240), fy(5240)], color=RULE, lw=1.2))
fig.text(fx(220), fy(5285),
 'Данные: ветровалы — 401 полигон по Республике Коми (1984–2026); рельеф — Copernicus DEM GLO-90; породный состав — Copernicus Forest Type 2019 (100 м);',
 **fp(14, SANS, 'normal', SUBT), va='center')
fig.text(fx(220), fy(5318),
 'ООПТ — OOPT AARI 2022; реки и озёра — OpenStreetMap, Natural Earth. Проекция: равновеликая Альберса, lon_0 = 54°E.  ·  #30DayMapChallenge 2026 · Day 13',
 **fp(14, SANS, 'normal', SUBT), va='center')

fig.savefig('build/poster_preview.png', dpi=72, facecolor=fig.get_facecolor())
fig.savefig('output/poster.png', dpi=DPI, facecolor=fig.get_facecolor())
fig.savefig('output/poster.pdf', facecolor=fig.get_facecolor())
fig.savefig('output/poster.jpg', dpi=DPI, facecolor=fig.get_facecolor(), pil_kwargs={'quality':93,'subsampling':0,'optimize':True})
print('ok')
