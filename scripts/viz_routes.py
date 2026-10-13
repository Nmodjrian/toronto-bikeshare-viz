"""Load modelled geometry and draw two-colour overlap maps."""
from pathlib import Path
import sqlite3,json
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import shape
from matplotlib.collections import LineCollection

ROOT=Path(__file__).resolve().parents[1]
COLORS={'Electric':'#00e5ff','Conventional':'#ff4fd8'}
BG='#050910'

def classify_bike(x):
    if pd.isna(x):return 'Unknown'
    x=str(x).upper().strip()
    if x.startswith('EFIT'):return 'Electric'
    if x=='ICONIC':return 'Conventional'
    return 'Unknown'

def load(year=2024,month=6):
    trips=pd.read_parquet(ROOT/f'data/processed/bikeshare_{year}_{month:02d}.parquet')
    with sqlite3.connect(ROOT/'data/processed/routes.sqlite') as db:
        routes=pd.read_sql_query('SELECT start_id,end_id,geometry_json FROM routes WHERE geometry_json IS NOT NULL',db)
    if routes.empty:raise ValueError('No successful routes. Run scripts/reconstruct_routes.py first.')
    geo=gpd.GeoDataFrame(routes.drop(columns='geometry_json'),geometry=[shape(json.loads(g)) for g in routes.geometry_json],crs='EPSG:4326').to_crs('EPSG:26917')
    for c,new in [('Start_Station_Id','start_id'),('End_Station_Id','end_id')]:
        trips[new]=trips[c].astype('string').str.strip().str.replace(r'\.0+$','',regex=True)
    trips['date']=pd.to_datetime(trips['Start_Time'],errors='coerce').dt.normalize()
    trips['bike_type']=trips['Bike_Model'].map(classify_bike) if 'Bike_Model' in trips else 'Unknown'
    trips=trips[trips.bike_type.isin(COLORS)&trips.date.notna()&trips.start_id.notna()&trips.end_id.notna()]
    trips=trips[(trips.start_id!=trips.end_id)&(pd.to_numeric(trips.Trip_Duration,errors='coerce')>0)]
    return trips,geo

def aggregate(trips,routes, daily=False):
    keys=(['date'] if daily else [])+['start_id','end_id','bike_type']
    counts=trips.groupby(keys,observed=True).size().rename('n').reset_index()
    result=counts.merge(routes,on=['start_id','end_id'],how='inner',validate='many_to_one')
    return gpd.GeoDataFrame(result,geometry='geometry',crs=routes.crs)

def plot(ax,frame,bounds,scale,title=None):
    ax.set_facecolor(BG)
    for kind in ('Conventional','Electric'):
        part=frame.loc[(frame.bike_type==kind)&frame.geometry.notna()].copy()
        part=part.loc[part.geometry.geom_type.eq('LineString')]
        if part.empty:continue
        seg=[np.asarray(g.coords) for g in part.geometry]
        widths=.20+1.05*np.log1p(part.n.to_numpy())/max(np.log1p(scale),1)
        for factor,alpha in [(7,.018),(3,.07),(1,.36)]:
            ax.add_collection(LineCollection(seg,colors=COLORS[kind],linewidths=widths*factor,alpha=alpha,rasterized=True))
    ax.set_xlim(bounds[0],bounds[2]);ax.set_ylim(bounds[1],bounds[3]);ax.set_aspect('equal');ax.axis('off')
    if title:ax.set_title(title,color='white',fontsize=17)
