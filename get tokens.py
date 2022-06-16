import pandas as pd
import re
from ckiptagger import WS


# 清除歌詞中多餘的符號
dataDF = pd.read_csv('./123.csv', encoding='utf8', index_col=0)
lyric = "&&&&&".join(dataDF.Lyric)
newLyric = re.sub("[\uf024\u3000\r\nRepeat ＊,＃,△,★]", "", lyric)

# 斷詞
path = "C:/Users/Hao/miniconda3/envs/NLP"  # 請自行更改為斷詞data所在的資料位置
ws = WS(f'{path}/data')

tokens = ws(newLyric.split("&&&&&"))

# 加入表格中
dataDF['Tokens'] = tokens

# 輸出成csv檔
dataDF.to_csv("lyric(tokens).csv")
