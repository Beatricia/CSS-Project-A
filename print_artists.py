import csv
from collections import defaultdict

data = list(csv.DictReader(open('data/lyrics_data/lyrics_with_sentiment_translated.csv', encoding='utf-8')))
a = defaultdict(lambda: {'country':'','pre':[],'post':[]})
for r in data:
    a[r['artist']]['country'] = r['country']
    if r['period'] in ('pre','post'):
        a[r['artist']][r['period']].append(float(r['compound']))

for artist, d in sorted(a.items(), key=lambda x: x[1]['country']):
    pre  = round(sum(d['pre'])  / len(d['pre']),  2) if d['pre']  else None
    post = round(sum(d['post']) / len(d['post']), 2) if d['post'] else None
    print(f"{d['country']:10} | {artist:25} | pre={str(pre):6} | post={post}")