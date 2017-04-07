import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix
from konlpy.tag import Kkma,Komoran
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.model_selection import train_test_split
from sklearn import linear_model
import os
import gensim
from collections import namedtuple
from gensim.models import doc2vec

def doc_merge(data):
    merged_docs = []

    for doc in data["document"]:
        merged_docs.append(doc)

    return merged_docs

def select_reviews(data, num, label):
    label_data = data[data.label == label].reset_index()
    index = np.random.randint(10000, size=num)
    return label_data.ix[index]


def token(doc):
    # kkma = Kkma()
    km = Komoran()
    pos_doc = []
    for doc_item in doc:
        for pos in km.pos(doc_item):
            if pos[1][0] == 'M':
                pos_doc.append(pos[0])
    return pos_doc

def select_reviews1(data):
    pos_review = data[data.label == 1]
    neg_review = data[data.label == 0]

    return pos_review,neg_review

def open_file2(name):
    with open('../review2/'+name+'.txt','r',encoding='utf-8',newline='\n') as f:
        date = []
        line = [file.split('\t')[1] for file in f.read().splitlines()]
        date.append(line)
        return date

sentiment_data = pd.read_csv("ratings_train.txt",sep='\t')
sentiment_data = sentiment_data.dropna()
#
positive_data, negative_data = select_reviews1(sentiment_data)
#
positive_merged_doc = doc_merge(positive_data)
negative_merged_doc = doc_merge(negative_data)
#
positive_pos = token(positive_merged_doc)
negative_pos = token(negative_merged_doc)
#
total_data = pd.concat((positive_data,negative_data))
X = total_data['document']
y = total_data['label']


model = doc2vec.Doc2Vec.load('doc2vec2.model')
print(model.docvecs[2])
vectorizer = CountVectorizer(min_df=1)
bow = vectorizer.fit_transform(X)
print(X)
print(y)
X_trn, X_tst, y_trn, y_tst = train_test_split(bow, y,test_size = 0.3)

# model 설정 및 평가
model = linear_model.LogisticRegression(penalty='l1')
model.fit(X_trn,y_trn)

y_pred = model.predict(X_tst)
conf_mat = confusion_matrix(y_tst,y_pred)

# #성능 평가
acc = (conf_mat[0,0] + conf_mat[1,1])/sum(sum(conf_mat))
print("accuracy = %f"%acc)
#
# #test 긍부정 분류
test_sentiment = ['꼭 보세요 강추합니다 한번 더 보고 싶은 영화에요',
                  '내가 이걸 왜 봤는지 모르겠다. 사전에 검색좀 해보고 볼걸 아.. 짜증나',
                 '졸잼 핵잼 최고 이런거 꼭봐야함 재미있음',
                 '왜봄? 망한듯 최악',]
#
vectorizer2 = CountVectorizer(min_df=1,vocabulary = vectorizer.vocabulary_)

new_input = vectorizer2.fit_transform(test_sentiment)

array = model.predict_proba(new_input.toarray())
print(array)