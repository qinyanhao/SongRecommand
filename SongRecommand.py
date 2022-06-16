import random
import numpy as np
import pandas as pd
from ckiptagger import WS
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer

# 讀取檔案
dataDF = pd.read_csv('./lyricDF(tokens).csv', encoding='utf8', index_col=0)


def getQueryTokens(query):
    '''query斷詞，並加進corpus中，回傳斷詞的series'''

    path = "C:/Users/Admin/miniconda3"  # 請自行更改為斷詞data所在的資料位置
    ws = WS(f"{path}/data")

    tokens = ws(query)

    # 把query文本加入coupus中
    tokenLIST=[]
    for token in tokens:
        tokenLIST.append(str(token))
    tokenSeries=pd.Series(tokenLIST)
    corpus=dataDF.Tokens.append(tokenSeries,ignore_index=True)

    return corpus


def recommand(corpus):
    vectorizer = TfidfVectorizer()
    tfidf_doc = vectorizer.fit_transform(
        raw_documents=corpus).toarray()  # 結果轉成陣列
    tfidfDF = pd.DataFrame(tfidf_doc)
    # len(vectorizer.vocabulary_)  #13025

    # TF-IDF向量置中
    tfidfDF = tfidfDF-tfidfDF.mean()

    # 維度縮減
    pca = PCA(n_components=20)
    pcaFit = pca.fit(tfidfDF)         # 減去平均值那個
    pca_topic_vectors = pcaFit.transform(tfidfDF)

    columns = [f"topic{i}" for i in range(pca.n_components)]

    pca_topic_vectorsDF = pd.DataFrame(pca_topic_vectors, columns=columns)

    # 計算各topic的標準差
    corpusSTD = pca_topic_vectorsDF.std()

    # 只考慮那些PCA>0的主題
    topic_pos = []
    for i in range(20):
        if pca_topic_vectorsDF.loc[len(pca_topic_vectorsDF)-1][i] > 0:
            topic_pos.append(
                (pca_topic_vectorsDF.loc[len(pca_topic_vectorsDF)-1][i], i))

    # 取出PCA最大的5個topic
    topic_fit = sorted(topic_pos, reverse=True)[:5]

    # 選擇在2個標準差以內歌曲

    std = []
    topicLIST = []
    for pca, i in topic_fit:
        std.append(pca + corpusSTD[i]*2)
        topicLIST.append(f'topic{i}')

    newDF = pca_topic_vectorsDF[(pca_topic_vectorsDF[topicLIST[0]] > 0) &
                                (pca_topic_vectorsDF[topicLIST[0]] <= std[0]) &
                                (pca_topic_vectorsDF[topicLIST[1]] > 0) &
                                (pca_topic_vectorsDF[topicLIST[1]] <= std[1]) &
                                (pca_topic_vectorsDF[topicLIST[2]] > 0) &
                                (pca_topic_vectorsDF[topicLIST[2]] <= std[2]) &
                                (pca_topic_vectorsDF[topicLIST[3]] > 0) &
                                (pca_topic_vectorsDF[topicLIST[3]] <= std[3]) &
                                (pca_topic_vectorsDF[topicLIST[4]] > 0) &
                                (pca_topic_vectorsDF[topicLIST[4]] <= std[4])]

    # 符合推薦的歌曲index
    indexLIST = (list(newDF.index))

    # 隨機選擇其中5首歌
    pick = random.choices(indexLIST, k=5)

    # 印出推薦歌曲
    print(f'推薦以下這五首歌：')
    print()
    for i in range(len(pick)):
        print(f'第{i+1}首', end="  ")
        print(dataDF.Singer[pick[i]], end="  ")
        print(dataDF.Title[pick[i]])
        print(dataDF.Lyric[pick[i]])
        print()
    print()


if __name__ == "__main__":
    # 請在此輸入想要推薦的內容。
    query = ['']

    corpus = getQueryTokens(query)
    recommand(corpus)
