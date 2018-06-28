import urllib
#from bs4 import BeautifulSoup
from multiprocessing import Pool

def count(s, w):
    c = 0
    for i in range(0, len(s) - len(w)):
        if s[i].isalpha() or s[i + len(w)].isalpha():
            continue
        else:
            if s[i:i + len(w)] == w:
                c += 1
    return c

def getSex(id):
    response = urllib.request.urlopen('https://www.imdb.com/name/{}/bio'.format(id))
    html = response.read()
    html = html.lower()
    shecount = count(html, 'she') + count(html, 'her')
    hecount = count(html, 'he') + count(html, 'his') + count(html, 'him')

    if shecount + hecount < 10:
        return None
    elif shecount > hecount:
        return 'F'
    else:
        return 'M'

def doit(id, birth):
    sex = getSex(id)
    print(id, sex)



def main():

    ##process imdb data https://www.imdb.com/interfaces/
    # lines = list(filter(None, open('name.basics.tsv','r').read().split('\n')))
    # newlines = []
    #
    # for line in lines:
    #     words = line.split('	')
    #     if len(words) != 6:
    #         continue
    #
    #     id = words[0]
    #     if not id.startswith('nm'):
    #         continue
    #     birth = None
    #     try:
    #         birth = int(words[2])
    #     except BaseException:
    #         continue
    #     newlines.append((id, birth))
    #
    # with open('strip.name', 'w') as f:
    #     for id, birth in newlines:
    #         f.write(str(id) + ' ' + str(birth) + '\n')

    newlines = [x.split() for x in list(filter(None, open('strip.name', 'r')
                .read().split('\n')))]

    for i in range(100):
        doit(newlines[i][0], newlines[i][1])


if __name__ == "__main__":
    main()
