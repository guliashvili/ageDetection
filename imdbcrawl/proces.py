lines = list(filter(None, open('name.basics.tsv','r').read().split('\n')))
newlines = []
count = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

for line in lines:
    words = line.split('	')
    if len(words) != 6:
        print('wutt')
        continue

    id = words[0]
    if not id.startswith('nm'):
        print('wut')
        continue
    birth = None
    try:
        birth = int(words[2])
    except BaseException:
        continue
    newlines.append((words[5].count(','), id, birth))
    count[words[5].count(',')] += 1

newlines = sorted(newlines, reverse=True)
print(newlines[:100])


print(count)
