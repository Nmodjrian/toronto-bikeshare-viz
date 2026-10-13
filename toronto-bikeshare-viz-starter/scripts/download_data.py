"""Discover and download official Bike Share Toronto annual ZIP (no URL guessing)."""
import argparse
from pathlib import Path
import requests

API = 'https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action/package_show'
DATASET = 'bike-share-toronto-ridership-data'

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--year', type=int, default=2024)
    ap.add_argument('--dest', type=Path, default=Path('data/raw'))
    args = ap.parse_args()
    r = requests.get(API, params={'id': DATASET}, timeout=60)
    r.raise_for_status()
    metadata = r.json()
    if not metadata.get('success'):
        raise RuntimeError('CKAN did not return a successful response')
    target = f'bikeshare-ridership-{args.year}.zip'
    matches = [x for x in metadata['result']['resources']
               if target in (x.get('name') or '') or target in (x.get('url') or '')]
    if not matches:
        raise RuntimeError(f'No official ZIP resource found for {args.year}; inspect the dataset catalogue.')
    url = matches[0]['url']
    args.dest.mkdir(parents=True, exist_ok=True)
    dest = args.dest / target
    print('Source:', url)
    with requests.get(url, stream=True, timeout=120) as response:
        response.raise_for_status()
        with dest.open('wb') as f:
            for chunk in response.iter_content(chunk_size=1024*1024):
                if chunk:
                    f.write(chunk)
    import zipfile
    if not zipfile.is_zipfile(dest):
        raise RuntimeError(f'Download is not a ZIP archive: {dest}')
    with zipfile.ZipFile(dest) as z:
        bad = z.testzip()
        if bad:
            raise RuntimeError(f'Corrupt ZIP member: {bad}')
    print('Saved and verified:', dest)

if __name__ == '__main__':
    main()
