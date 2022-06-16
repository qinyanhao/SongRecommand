import pandas as pd
import re
import requests
from bs4 import BeautifulSoup


def getSingerDICT():
    '''抓熱門男歌手頁面網址，回傳{歌手名:網址}的字典'''

    urls = {}
    u = 'http://mojim.com/twza1.htm'
    res = requests.get(u)
    soup = BeautifulSoup(res.text, "html.parser")
    result = soup.find("ul", class_="s_listA")

    for e in result.find_all("a"):
        domin = "http://mojim.com"
        url = domin+e['href']
        name = e['title'].split()[0]
        urls[name] = url

    return urls


def getSongDICT(url):
    '''抓該歌手所有被標示為「國語」專輯的歌曲網址，回傳{歌名:網址}的字典'''
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    result1 = soup.find_all("dd", "hb2")
    result2 = soup.find_all("dd", "hb3")

    songsURL = {}
    for r in result1:
        if r.find("span", "hc2").text[:2] == "國語":
            domin = "http://mojim.com"
            for e in r.find("span", "hc3").find_all("a"):
                if e.text not in songsURL.keys():
                    songsURL[e.text] = domin+e['href']
                else:
                    continue

            for e in r.find("span", "hc4").find_all("a"):
                if e.text not in songsURL.keys():
                    songsURL[e.text] = domin+e['href']
                else:
                    continue

    for r in result2:
        if r.find("span", "hc2").text[:2] == "國語":
            domin = "http://mojim.com"
            for e in r.find("span", "hc3").find_all("a"):
                if e.text not in songsURL.keys():
                    songsURL[e.text] = domin+e['href']
                else:
                    continue

            for e in r.find("span", "hc4").find_all("a"):
                if e.text not in songsURL.keys():
                    songsURL[e.text] = domin+e['href']
                else:
                    continue

    return songsURL


def getLyric(url):
    '''抓歌名歌詞內容，回傳(title, lyric)的tuple形式，type都是string'''

    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    # 抓歌名
    title = soup.find('title').text.split()[0]

    # 抓歌詞
    result = str(soup.find('dd', 'fsZx3')).split('<br/>')

    # 清除多餘資訊
    removeIndex = []
    for e in result:
        if '：' in e:
            removeIndex.append(result.index(e))
        elif e.startswith("<"):
            removeIndex.append(result.index(e))
        elif e.endswith("</a>"):
            removeIndex.append(result.index(e))
        elif e.endswith("</dd>"):
            removeIndex.append(result.index(e))
    removeIndex.reverse()
    for i in removeIndex:
        del result[i]

    # 清除動態歌詞
    index = []
    for e in result:
        if e.startswith('['):
            index.append(result.index(e))
    # 確認是否有動態歌詞需刪除
    if index != []:
        del result[index[0]:]

    # 清除空字串
    removeSpace = []
    while("" in result):
        result.remove("")

    # 存成一個string
    lyric = " ".join(result)

    return (title, lyric)


import pandas as pd
import re
import requests
from bs4 import BeautifulSoup


# 取得所有男歌手的歌曲網址
# {歌手:{歌名:網址}}
allSongsURL = {}
for key, val in getSingerDICT().items():
    allSongsURL[key] = getSongDICT(val)

# 取得所有歌曲歌詞
# {歌手:[(歌名:歌詞)]}
allLyric = {}
for key, val in allSongsURL.items():
    songLIST = []
    for url in val.values():
        lyric = getLyric(url)
        songLIST.append(lyric)

    allLyric[key] = songLIST


titleLIST = []
lyricLIST = []
for key, val in allLyric.items():
    for t in allLyric[key]:
        titleLIST.append(t[0])
        lyricLIST.append(t[1])
        
# 整理內容
newLyricLIST = []
for e in lyricLIST:
    newLyric = re.sub("ㄧ", "一", e)
    newLyricLIST.append(newLyric)

# 歌手清單
songAmount = []
for k in allLyric.keys():
    songAmount.append(len(allLyric[k]))
singerLIST = []
for i in range(len(songAmount)):
    count = 0
    while count < songAmount[i]:
        singerLIST.append(list(allLyric.keys())[i])
        count += 1


# 製作成表格
DF = pd.DataFrame(singerLIST, columns=["Singer"])
DF['Title'] = titleLIST
DF['Lyric'] = newLyricLIST

# 因為有些歌曲是純音樂所以沒有歌詞，移除那些無歌詞的歌曲
emptyIntex=[]                          #找出沒有歌詞的那行的index
for i, e in enumerate(DF['Lyric']):
    if len(e) <10:
        emptyIntex.append(i)

# 刪除該行
newDF = DF.drop(index=emptyIntex)

# 重新編號
newDF.reset_index(drop=True, inplace=True)

# 輸出成CSV檔
newDF.to_csv("lyric.csv")