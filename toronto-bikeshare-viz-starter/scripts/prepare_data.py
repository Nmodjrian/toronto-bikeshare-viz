"""Extract one month from official annual ridership archive to Parquet."""
import argparse
from pathlib import Path
import zipfile
import pandas as pd

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--year', type=int, default=2024)
    ap.add_argument('--month', type=int, default=6)
    args = ap.parse_args()
    if args.month not in range(1,13):
        ap.error('--month must be 1..12')
    src = Path(f'data/raw/bikeshare-ridership-{args.year}.zip')
    dst = Path(f'data/processed/bikeshare_{args.year}_{args.month:02d}.parquet')
    dst.parent.mkdir(parents=True, exist_ok=True)
    selected=[]
    with zipfile.ZipFile(src) as z:
        members=[n for n in z.namelist() if n.lower().endswith('.csv')]
        if len(members)!=1:
            raise RuntimeError(f'Expected exactly one annual CSV in ZIP; found {members}')
        with z.open(members[0]) as stream:
            for chunk in pd.read_csv(stream,chunksize=100_000,low_memory=False,
                       dtype={'Start_Station_Id':'string','End_Station_Id':'string'}):
                if 'Start_Time' not in chunk:
                    raise KeyError('Start_Time column absent; annual schema may have changed')
                mask=chunk['Start_Time'].astype('string').str.startswith(f'{args.year}-{args.month:02d}-',na=False)
                if mask.any():
                    selected.append(chunk.loc[mask].copy())
    if not selected:
        raise RuntimeError('No records match the requested month')
    df=pd.concat(selected,ignore_index=True)
    for col in ['Start_Station_Id','End_Station_Id']:
        if col in df:
            df[col]=df[col].astype('string').str.strip().str.replace(r'\.0+$','',regex=True)
    for col in ['Start_Time','End_Time']:
        if col in df:
            df[col]=pd.to_datetime(df[col],errors='coerce')
    if 'Trip_Duration' in df:
        df['Trip_Duration']=pd.to_numeric(df['Trip_Duration'],errors='coerce')
    df.to_parquet(dst,index=False)
    print(f'{len(df):,} records saved to {dst}')

if __name__=='__main__':
    main()
