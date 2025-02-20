ME = 0
SUL = 15


import urllib.request
from bs4 import BeautifulSoup
from multiprocessing import Pool
import multiprocessing
import time
import json
import sys



def count(s, w):
    c = 0
    for i in range(0, len(s) - len(w) - 1):
        if s[i].isalpha() or s[i + len(w) + 1].isalpha():
            continue
        else:
            if s[i + 1:i + len(w) + 1] == w:
                c += 1
    return c

def getSex(id):
    while True:
        try:
            response = urllib.request.urlopen('https://www.imdb.com/name/{}/bio'.format(id))
        except:
            print("Unexpected error:", sys.exc_info()[0])
            print('sleeping https://www.imdb.com/name/{}/bio'.format(id))
            time.sleep(60)
            continue

        if response.getcode() != 200:
            print('sleeping https://www.imdb.com/name/{}/bio'.format(id))
            time.sleep(60)
        else:
            break

    html = response.read().decode('utf-8')
    html = html.lower()
    shecount = count(html, 'she') + count(html, 'her') + count(html, 'actress')
    hecount = count(html, 'he') + count(html, 'his') + count(html, 'him') + count(html, 'actor')


    if shecount - 2 > hecount:
        return 'F'
    elif hecount - 2 > shecount:
        return 'M'
    else:
        return None

def get_img_link(src):
    if not src.endswith('.jpg'):
        print(src[-4])
        return None

    while len(src) > 0 and not src.endswith('V1_'):
        src = src[:-1]

    if len(src) == 0:
        return None
    src += '.jpg'

    return src


def get_year(alt):
    for i in range(len(alt) - 3):
        sub = alt[i : i + 4]
        if not sub.isdigit():
            continue

        year = int(sub)
        if year < 1800 or year > 2018:
            continue

        if i + 4 < len(alt) and alt[i + 4].isalpha():
            continue

        return year

    return None


def get_pic(ahref):
    img = ahref.find_all('img', alt=True, src=True)
    if len(img) != 1:
        return None
    img = [i for i in img][0]
    alt = img['alt']
    src = img['src']

    img = get_img_link(src)
    if img is None:
        return None

    year = get_year(alt)
    if year is None:
        return None

    return (img, year)


def imgspage(id, page):
    lst = []
    url = 'https://www.imdb.com/name/{}/mediaindex?page={}'.format(id, page)
    while True:
        try:
            response = urllib.request.urlopen(url)
        except:
            print("Unexpected error:", sys.exc_info()[0])
            print('sleeping https://www.imdb.com/name/{}/mediaindex?page={}'.format(id, page))
            time.sleep(60)
            continue

        if response.getcode() != 200:
            print('sleeping https://www.imdb.com/name/{}/mediaindex?page={}'.format(id, page))
            time.sleep(60)
        else:
            break

    html = response.read().decode('utf-8')
    soup = BeautifulSoup(html, 'lxml')

    div_avatars = soup.findAll("div", {"class": "media_index_thumb_list"})
    if len(div_avatars) != 1:
        return []

    div_avatars = [x for x in div_avatars][0]

    separate_avatars = div_avatars.find_all('a', href=True)

    for separate_avatar in separate_avatars:
        g = get_pic(separate_avatar)
        if g is not None:
            lst.append(g)

    return lst


def imgs(id):
    lst = []
    i = 1
    while True:
        r = imgspage(id, i)
        if len(r) == 0:
            break
        lst += r
        i += 1

    return lst


def doit(idbirth):
    id = idbirth[0]
    birth = idbirth[1]
    print(id,'-')

    img_lst = imgs(id)
    if len(img_lst) == 0:
        return None
    img_lst = [(img, year - birth) for img, year in img_lst]

    sex = getSex(id)
    if sex is None:
        return None

    ret = {id: (sex, img_lst)}
    print(id,'+')
    return ret


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

    newlines = [(x.split()[0], int(x.split()[1])) for x in list(filter(None, open('strip.name', 'r')
                .read().split('\n')))]

    data = []
    le = len(newlines)
    s = int(le * ME / SUL)
    e = min(le, int(le * (ME + 1) / SUL))
    for i in range(s, e):
        res = doit(newlines[i])
        if res is not None:
            data.append(res)
        if len(data) % 10 == 0:
            sys.stdout.flush()

    with open('data{}.txt'.format(ME), 'w') as f:
        json.dump(data, f, ensure_ascii=False)



if __name__ == "__main__":
    main()
