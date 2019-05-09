
import json
import glob
import sys
import re, string, unicodedata
import nltk
import contractions
import inflect
# from bs4 import BeautifulSoup
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

#/Users/Dana/Downloads/CS273_Project/scandal/postprocessing7/college_admissions_scandal/Posts@from@2019-03-14@to@2019-03-14@(13)


#split the files into respective folders
os.mkdir("/Users/Dana/Downloads/CS273_Project/scandal/postprocessing/")
for folder in glob.glob(str(sys.argv[1])+"/*"):
    postprocess_folder = "/Users/Dana/Downloads/CS273_Project/scandal/postprocessing/" + os.path.splitext(os.path.basename(folder))[0] + "/"
    os.mkdir(postprocess_folder)

    for file in glob.glob(folder+"/*.tsv"):
        file_name = (os.path.splitext(os.path.basename(file))[0])
        print(file_name)
        print(postprocess_folder+file_name)
        with open(file, "rU",encoding="utf-8") as inputf, open((postprocess_folder+file_name+"_processed.tsv"), "a", encoding='utf-8') as outputf:
        # with open(file, "rU",encoding="utf-8") as inputf:
        
            # print(inputf)
            reader = csv.reader(inputf, delimiter="\t")
            writer = csv.writer(outputf, delimiter = "\t")
            
            header = next(reader, None)
            writer.writerow(header)
            # print(header)
            for line in reader:
                try:
                    loaded_data = line[3].encode("utf-8", errors="ignore")
                    tweet_text = (loaded_data).strip().decode('utf-8', 'ignore')
                    # tweet_text = tweet_text.encode('utf-8')
                    tweet_text = replace_contractions(tweet_text).lower()
                    # # tweet_text = tweet_text.decode('utf-8')
                    # # print(tweet_text)
                    # # tweet_text = denoise_text(tweet_text)
                    words = tweet_text.split()
                    words = remove_non_ascii(words)
                    tweet_text = " ".join(words)
                    tweet_text = re.sub(r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))''', " ", tweet_text)
                    # print(tweet_text)
                    line[3] = tweet_text.encode("utf-8", errors="ignore").strip()
                    # print(tweet_text)
                    writer.writerow(line)
                except Exception as e:
                    print(e)

                    with open("/Users/Dana/Downloads/CS273_Project/scandal/preprocessing/errors.txt", "a") as errorf:
                        errorf.write(file_name + "   " + str(e)+"\n")
                    # try:
                    #     print(loaded_data["error"])
                    # except Exception as error_again:
                    #     print(error_again)
                    continue

                

        
