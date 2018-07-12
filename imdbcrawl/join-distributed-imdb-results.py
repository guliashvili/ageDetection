import json
import pickle

ans = []
for i in range(0, 15):
    file = "data/data{}.txt".format(i)
    x = json.loads(open(file, 'r').read())
    ans += x

with open('data.txt', 'w') as f:
    json.dump(ans, f, ensure_ascii=False, separators=(',',':'))
