import re
import pickle
import numpy as np
import pandas as pd
import torch
from string import punctuation
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import sent_tokenize, word_tokenize 
from sklearn.feature_extraction.text import CountVectorizer
from flask import Flask, render_template, request

# import MLP module definition
from models import MLP

# load saved model parameters and vectorizers
model = pickle.load(open('web-app/data/model.pkl', 'rb'))
title_vectorizer = pickle.load(open('web-app/data/title_vectorizer.pkl','rb'))
text_vectorizer = pickle.load(open('web-app/data/text_vectorizer.pkl','rb'))


def preprocess(df):
    lemmatizer = WordNetLemmatizer()

    text_processed = []
    for text in df.text:
        # remove punctuation and lowercase
        text = re.sub(r'[^a-zA-Z]', ' ', text) 
        text = text.lower()
        
        # tokenize and lemmatize tokens
        tokens = word_tokenize(text)
        tokens = [lemmatizer.lemmatize(x) for x in tokens]
        text_processed.append(' '.join(tokens))
 

    title_processed = []
    for title in df.title:
        # remove punctuation and lowercase
        title = re.sub(r'[^a-zA-Z]', ' ', title) 
        title = title.lower()
        
        # tokenize and lemmatize tokens
        tokens = word_tokenize(title)
        tokens = [lemmatizer.lemmatize(x) for x in tokens]
        title_processed.append(' '.join(tokens))
        
    # vectorize
    text_matrix = text_vectorizer.transform(text_processed).toarray()
    title_matrix = title_vectorizer.transform(title_processed).toarray()
    
    # return np matrix
    X = np.concatenate([title_matrix, text_matrix], axis=1)
    return X

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/predict', methods=['POST'])
def predict():
    title = request.form['title']
    text = request.form['text']
    d = {'title': [title], 'text': [text]}

    # create dataframe from user input
    X_df = pd.DataFrame(data=d)

    # preprocess df and return np array
    X_np = preprocess(X_df)

    # convert to tensor
    X_tensor = torch.Tensor(X_np)

    # predict
    y_pred = model(X_tensor)
    y_pred_max = torch.max(y_pred,1)[1]
    print(y_pred, y_pred_max)
    if y_pred_max == 0:
        my_prediction = "Real news!"
    else:
        my_prediction = "Fake news!"
    return render_template('result.html', prediction=my_prediction)

if __name__ == '__main__':
    app.run()