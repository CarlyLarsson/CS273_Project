#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import json
import glob
import sys
import re, string, unicodedata
import nltk
import contractions
import inflect
from bs4 import BeautifulSoup
from nltk import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import LancasterStemmer, WordNetLemmatizer
import os
import csv
#https://www.kdnuggets.com/2018/03/text-data-preprocessing-walkthrough-python.html
def strip_html(text):
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text()

def denoise_text(text):
    text = strip_html(text)
    return text

def replace_contractions(text):
    """Replace contractions in string of text"""
    return contractions.fix(text)

def remove_non_ascii(words):
    """Remove non-ASCII characters from list of tokenized words"""
    new_words = []
    for word in words:
        new_word = unicodedata.normalize('NFKD', word).encode('ascii', 'ignore').decode('utf-8', 'ignore')
        new_words.append(new_word)
    return new_words



#split the files into respective folders
for folder in glob.glob(str(sys.argv[1])+"/*"):
    for file in glob.glob(folder+"/*."):
        file_name = (os.path.splitext(os.path.basename(file))[0])
        with open(file, "rU") as inputf:
            for line in inputf:
                loaded_data = json.loads(line)
                try:
                    tweet_text = (loaded_data["text"]).strip()
                    # print(tweet_text)
                    # tweet_text = denoise_text(tweet_text)
                    tweet_text = tweet_text.encode('utf-8')
                    tweet_text = replace_contractions(tweet_text).lower()
                    tweet_text = tweet_text.decode('utf-8')
                    words = tweet_text.split()
                    words = remove_non_ascii(words)
                    tweet_text = " ".join(words)
                    tweet_text = re.sub(r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))''', " ", tweet_text)
                    tweet_text = tweet_text.strip()
                    with open((folder+"/"+file_name+".txt"), "a") as outputf:
                        outputf.write(tweet_text)
                        outputf.write("\n")
                except Exception as e:
                    print(e)
                    try:
                        print(loaded_data["error"])
                    except Exception as error_again:
                        print(error_again)
                    continue

                

        
