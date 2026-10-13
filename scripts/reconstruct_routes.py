"""Compute distinct OD bike routes using a local GraphHopper server; resumable SQLite cache.

For an approachable sample use --max-pairs 2000. --max-pairs 0 routes all pairs.
Routes are modelled and use present-day stations + OSM unless historic sources provided.
"""
from pathlib import Path
import argparse,json,sqlite3,time
import pandas as pd
import requests

ROOT=Path(__file__).resolve().parents[1]
def norm(s): return s.astype('string').str.strip().str.replace(r'\.0+$','',regex=True)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--year',type=int,default=2024)
    ap.add_argument('--month',type=int,default=6)
    ap.add_argument('--max-pairs',type=int,default=2000,help='0 for all unique pairs')
    ap.add_argument('--url',default='http://127.0.0.1:8989')
    ap.add_argument('--pause',type=float,default=0)
    a=ap.parse_args()
    trips=pd.read_parquet(ROOT/f'data/processed/bikeshare_{a.year}_{a.month:02d}.parquet')
    stations=pd.read_csv(ROOT/'data/processed/stations_current.csv',dtype={'station_id':'string'})
    if not {'Start_Station_Id','End_Station_Id','Trip_Duration'}.issubset(trips):
        raise ValueError('Missing station ID or trip duration columns')
    trips['start_id']=norm(trips.Start_Station_Id)
    trips['end_id']=norm(trips.End_Station_Id)
    trips=trips[(trips.start_id!=trips.end_id)&(pd.to_numeric(trips.Trip_Duration,errors='coerce')>0)].dropna(subset=['start_id','end_id'])
    pairs=trips.groupby(['start_id','end_id']).size().rename('trip_count').reset_index()
    s=stations.set_index('station_id')[['lat','lon']]
    pairs=pairs.join(s,on='start_id').rename(columns={'lat':'slat','lon':'slon'})
    pairs=pairs.join(s,on='end_id').rename(columns={'lat':'elat','lon':'elon'}).dropna(subset=['slat','slon','elat','elon'])
    pairs=pairs.sort_values('trip_count',ascending=False,kind='stable')
    if a.max_pairs>0:pairs=pairs.head(a.max_pairs)
    outfile=ROOT/'data/processed/routes.sqlite';outfile.parent.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(outfile)
    db.execute("""CREATE TABLE IF NOT EXISTS routes (start_id TEXT NOT NULL,end_id TEXT NOT NULL,
    distance_m REAL,time_min REAL,geometry_json TEXT,error TEXT,PRIMARY KEY(start_id,end_id))""")
    session=requests.Session(); total=ok=fail=skip=0
    for p in pairs.itertuples(index=False):
        total+=1
        if db.execute('SELECT 1 FROM routes WHERE start_id=? AND end_id=?',(p.start_id,p.end_id)).fetchone():
            skip+=1;continue
        params=[('point',f'{p.slat},{p.slon}'),('point',f'{p.elat},{p.elon}'),('profile','bike'),('points_encoded','false'),('instructions','false')]
        try:
            response=session.get(a.url.rstrip('/')+'/route',params=params,timeout=35);response.raise_for_status()
            path=response.json()['paths'][0]
            geom=path['points']
            if geom.get('type')!='LineString':raise ValueError('Unexpected geometry')
            values=(p.start_id,p.end_id,path['distance'],path['time']/60000,json.dumps(geom),None)
            ok+=1
        except (requests.RequestException,ValueError,KeyError,IndexError,TypeError) as exc:
            values=(p.start_id,p.end_id,None,None,None,str(exc)[:300]);fail+=1
        db.execute('INSERT OR REPLACE INTO routes VALUES (?,?,?,?,?,?)',values)
        if (ok+fail)%100==0:db.commit();print(f'processed {ok+fail}; errors {fail}; cached {skip}',flush=True)
        if a.pause:time.sleep(a.pause)
    db.commit();db.close()
    print(f'Considered {total:,} OD pairs | newly routed {ok:,} | failed {fail:,} | previously cached {skip:,}')
    print('Route database:',outfile)
    if fail:print('Failed pairs can be retried by deleting their rows from routes.sqlite.')
if __name__=='__main__':main()
