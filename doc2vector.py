import multiprocessing
import pandas as pd
from ckiptagger import WS
from gensim.models.doc2vec import TaggedDocument, Doc2Vec


# 讀取檔案
corpusDF=pd.read_csv("./lyricDF.csv")

# 斷詞

pth = "C:/Users/Admin/miniconda3"  # 請自行更改為斷詞data所在的資料位置
ws = WS(f"{pth}/data")

tokens = ws(corpusDF.Lyric)

tokenizedSong = []

for token in tokens:
    tokenizedSong.append(' '.join(token))

# Doc2vec

             #看CPU有多少核心可以用
number_cors = multiprocessing.cpu_count()

corpus = tokenizedSong
training_corpus = []
for i, text in enumerate(corpus):

    tagged_doc = TaggedDocument(text, [i])               
    training_corpus.append(tagged_doc)

# 用 10 做為窗口大小及100做為詞向量的維度
# .min_count 是詞彙的最小文本頻率
# 建立模型
# size 改稱：vector_size；iter 改稱：epochs

model = Doc2Vec(vector_size=100, window=10, min_count=2, workers=number_cors, epochs=10)

# 訓練模型前先編輯詞彙
model.build_vocab(training_corpus)

# 進行10個世代的訓練
model.train(training_corpus, total_examples=model.corpus_count, epochs=model.epochs)


def recommand(query):

    # query斷詞
    inqTokens = ws(query)
    inqTokenized =' '.join(sum(inqTokens,[]))

    # 輸出結果
    print(f"輸入段落：{inqTokenized}")
    print()

    inferred_vector = model.infer_vector(doc_words=[inqTokenized], epochs=10)

    # dv = docvecs
    sims = model.docvecs.most_similar([inferred_vector], topn=5)
    n=1

    print("以下是推薦的歌曲:")
    for count, sim in sims:
        print(f'第{n}首  {corpusDF.Singer[count]}  {corpusDF.Title[count]}')
        print(f'{corpusDF.Lyric[count]}')
        print()
        print()
        n+=1


if __name__ == "__main__":
    
    # 請在此輸入想要推薦的內容。
    query=['請推薦我快樂的歌。']
    recommand(query)