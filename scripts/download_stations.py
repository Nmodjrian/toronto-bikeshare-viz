"""Download contemporary Toronto GBFS station coordinates (not historical)."""
from pathlib import Path
from datetime import datetime, timezone
import json
import requests
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
GBFS = "https://toronto.publicbikesystem.net/customer/gbfs/v3.0/gbfs.json"

def main():
    r=requests.get(GBFS,timeout=45);r.raise_for_status()
    j=r.json(); feeds=j.get('data',{}).get('feeds',[])
    info=next((f['url'] for f in feeds if f['name']=='station_information'),None)
    if not info: raise RuntimeError('Station information not found in GBFS auto-discovery feed')
    r=requests.get(info,timeout=45);r.raise_for_status()
    station_list=r.json()['data']['stations']
    df=pd.DataFrame([dict(station_id=str(x['station_id']),lon=x['lon'],lat=x['lat']) for x in station_list])
    if df.station_id.duplicated().any(): raise ValueError('Duplicate station IDs in GBFS')
    dest=ROOT/'data/processed/stations_current.csv';dest.parent.mkdir(parents=True,exist_ok=True)
    df.to_csv(dest,index=False)
    meta=ROOT/'data/processed/stations_current_metadata.json'
    meta.write_text(json.dumps({'retrieved_utc':datetime.now(timezone.utc).isoformat(),'source':info,'station_count':len(df),'warning':'Not historically validated for 2024'},indent=2))
    print('Wrote',dest,'with',len(df),'contemporary stations')
if __name__=='__main__':main()
