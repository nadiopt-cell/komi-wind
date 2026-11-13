# -*- coding: utf-8 -*-
import numpy as np, geopandas as gpd, sys, math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection, LineCollection
from matplotlib import colors as mcolors
from matplotlib import patheffects as pe
from PIL import Image
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
LK_V=[np.asarray(p.exterior.coords) for p in polys_of(lk)]
OOPS_V=[np.asarray(p.exterior.coords) for p in polys_of(oopt)]
WCOL=[mcolors.to_rgba(c) for c in RAMP]
WP=[];WC=[]
for g,per in zip(wf.geometry,wf['period']):
    i=PERIODS.index(per) if per in PERIODS else 0
    if g.geom_type=='Polygon': WP.append(g);WC.append(WCOL[i])
    elif g.geom_type=='MultiPolygon':
        for p in g.geoms: WP.append(p);WC.append(WCOL[i])
WP_V=[np.asarray(p.exterior.coords) for p in WP]
AR=[np.asarray(g.coords) for g in arr.geometry]
AR_COL=[WCOL[PERIODS.index(p)] if p in PERIODS else (1,1,1,1) for p in arr['period']]
AR_HCOL=[WCOL[PERIODS.index(p)] if p in PERIODS else (1,1,1,1) for p in heads['period']]
RIV={0.42:[],0.6:[],0.8:[]}
for g,wv in zip(rv.geometry,rv['width']):
    if g.geom_type=='LineString': RIV[wv].append(np.asarray(g.coords))
    elif g.geom_type=='MultiLineString': RIV[wv].extend([np.asarray(p.coords) for p in g.geoms])
KOMI=[]
kg=komi.geometry.iloc[0]
for g in (kg.geoms if hasattr(kg,'geoms') else [kg]):
    KOMI.append(np.asarray(g.exterior.coords)); KOMI.extend([np.asarray(r.coords) for r in g.interiors])
TRI=[]
for g,b in zip(heads.geometry, heads['bearing']):
    x,y=g.x,g.y; th=np.deg2rad(b); L=2700; Wd=1150
    ux,uy=np.sin(th),np.cos(th); vx,vy=np.cos(th),-np.sin(th)
    TRI.append([(x-ux*L+vx*Wd/2,y-uy*L+vy*Wd/2),(x,y),(x-ux*L-vx*Wd/2,y-uy*L-vy*Wd/2)])

REL=np.asarray(Image.open('build/relief_full.png').convert('RGB'))
FOR=np.asarray(Image.open('build/forest_aea.png').convert('RGBA'))
EX0,EY0,EX1,EY1=-486000.0,-462000.0,496000.0,306000.0

from pyproj import Transformer
t=Transformer.from_crs(4326,AEA,always_xy=True)
cities=[('Сыктывкар',50.836,61.668,10,-10,'right'),('Ухта',53.684,63.567,9,4,'left'),
        ('Печора',57.224,65.145,9,2,'left'),('Вуктыл',57.316,63.857,9,2,'left'),
        ('Усть-Кулом',53.687,61.689,9,2,'left'),('Троицко-Печорск',56.190,62.716,9,8,'left'),
        ('Усть-Цильма',52.193,65.438,9,2,'left'),('Объячево',49.633,60.333,-11,8,'right')]

W_PX,H_PX=1800,1408
fig=plt.figure(figsize=(W_PX/150,H_PX/150),dpi=150)
fig.patch.set_facecolor('#FBF8F2')
ax=fig.add_axes([0.02,0.075,0.96,0.825])
ax.set_xlim(EX0,EX1); ax.set_ylim(EY0,EY1); ax.set_aspect('equal'); ax.axis('off')

def fp(size,family='Segoe UI',weight='normal',color='#241F1A',style='normal'):
    return dict(family=family,fontsize=size,fontweight=weight,color=color,fontstyle=style)
def halo(w=3.5,c='#FBF8F2'): return [pe.withStroke(linewidth=w,foreground=c)]

def draw(step):
    ax.clear(); ax.set_xlim(EX0,EX1); ax.set_ylim(EY0,EY1); ax.set_aspect('equal'); ax.axis('off')
    ax.imshow(REL,extent=(X0,X1,Y0,Y1),origin='upper',zorder=0,interpolation='lanczos')
    if step>=2:
        ax.imshow(FOR,extent=(X0,X1,Y0,Y1),origin='upper',zorder=1,interpolation='lanczos',alpha=0.42)
    if step>=4:
        ax.add_collection(PolyCollection(LK_V,facecolors='#BBD0D9',edgecolors='#8FB0BE',linewidths=0.3,zorder=2,alpha=0.9))
        for wv,lw,al,col in [(0.42,0.26,0.3,'#7FA0B2'),(0.6,0.45,0.45,'#6B93A8'),(0.8,0.8,0.75,'#577F97')]:
            if RIV[wv]: ax.add_collection(LineCollection(RIV[wv],colors=col,linewidths=lw,alpha=al,zorder=2.5,capstyle='round'))
    if step>=3:
        ax.add_collection(PolyCollection(OOPS_V,facecolors='#2F6F6B',edgecolors='none',alpha=0.13,zorder=3))
        ax.add_collection(PolyCollection(OOPS_V,facecolors='none',edgecolors='#14514E',linewidths=0.7,alpha=0.95,linestyles=(0,(3,2)),zorder=3.1))
    if step>=5:
        ax.add_collection(PolyCollection(WP_V,facecolors='none',edgecolors='#FBF8F2',linewidths=1.0,alpha=0.5,zorder=3.9))
        ax.add_collection(PolyCollection(WP_V,facecolors=WC,edgecolors='#3B1027',linewidths=0.35,alpha=0.97,zorder=4))
    if step>=6:
        ax.add_collection(LineCollection(AR,colors='#241F1A',linewidths=3.4,alpha=0.42,zorder=5,capstyle='round'))
        ax.add_collection(LineCollection(AR,colors=AR_COL,linewidths=1.9,alpha=1.0,zorder=5.1,capstyle='round'))
        ax.add_collection(PolyCollection(TRI,facecolors=AR_HCOL,edgecolors='#241F1A',linewidths=1.0,zorder=5.3))
    ax.add_collection(LineCollection(KOMI,colors='#241F1A',linewidths=1.5,alpha=0.9,zorder=6))
    for name,lon,lat,dx,dy,ha in cities:
        x,y=t.transform(lon,lat)
        if not (EX0<x<EX1 and EY0<y<EY1): continue
        ax.plot([x],[y],marker='o',ms=4.5,mfc='#FBF8F2',mec='#241F1A',mew=1.6,zorder=9)
        ax.annotate(name,xy=(x,y),xytext=(dx,dy),textcoords='offset points',ha=ha,va='center',
                    **fp(13,'Segoe UI','semibold','#241F1A'),zorder=9,path_effects=halo(3))
    # caption
    labels=['Рельеф','Породный состав леса','ООПТ','Реки и озёра','Ветровалы 1984–2026','Направления ветра']
    fig.texts.clear()
    fig.text(0.02,0.978,'ВЕТЕР × РЕЛЬЕФ × ЛЕС',**fp(27,'Georgia','bold','#241F1A'),va='top')
    fig.text(0.02,0.942,'Interactions · Республика Коми · #30DayMapChallenge 2026 · Day 13',**fp(13.5,'Segoe UI','normal','#6F655A'),va='top')
    fig.text(0.98,0.978,f'{step}/6  ·  {labels[step-1]}',**fp(15,'Segoe UI','bold','#7A1C78'),ha='right',va='top')
    fig.text(0.02,0.022,'Ветровалы: 401 событие · 53 279 га · 1984–2026   |   Рельеф: Copernicus DEM GLO-90   |   Лес: Copernicus Forest Type 2019   |   ООПТ: OOPT AARI 2022',
             **fp(10.5,'Segoe UI','normal','#8A7F71'),va='bottom')
    fig.savefig(f'build/gif_{step}.png',dpi=150,facecolor=fig.get_facecolor())

for s in range(1,7):
    draw(s); print('frame',s,flush=True)
print('done')
