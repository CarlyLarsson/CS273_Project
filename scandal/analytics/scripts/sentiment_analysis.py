from empath import Empath
import csv 
from glob import glob
import sys
import os
import numpy as np
import pandas as pd
import re

def sent_analyze(tweet):
    lexicon = Empath()
    sent = lexicon.analyze(tweet, normalize=False)
    return sent

def empath_a_folder(folder_label, content_at):
    #print(sys.argv[1])
    for folder in glob(str(sys.argv[1])+"/*/*"):
        # print(os.path.splitext(os.path.basename(folder))[0])
        print(os.getcwd())
        cwd = os.getcwd()
        empath_folder = cwd + "/empath_{}/".format(folder_label) + os.path.splitext(os.path.basename(folder))[0] + "/"
        try:
            os.makedirs(empath_folder)
        except Exception as e:
            print(str(e))
            continue
        for file in glob(folder+"/*.tsv"):
            file_name = (os.path.splitext(os.path.basename(file))[0])
            print(file_name)
            exists = os.path.isfile(empath_folder+file_name+"_empath.tsv")
            if exists:
                continue
            with open(file, 'rU') as f, open(empath_folder+file_name+"_empath.tsv", 'w') as nf:
                tsvreader = csv.reader(f, delimiter='\t') 
                fields = next(tsvreader)
                tsvwriter = csv.writer(nf, delimiter='\t')
                resp = sent_analyze("this is great")
                for key in resp.keys():
                    fields.append(key)
                tsvwriter.writerow(fields)

                for row in tsvreader: 
                    tweet = row[content_at]
                    empath_reading = sent_analyze(tweet)
                    for result in empath_reading.values():
                        row.append(result)
                    tsvwriter.writerow(row)

def totaling_a_folder(sentiment_at):
    #Go through all the given tweets empath results and return the top 10 category scoreres
    fields = []
    totaling = np.zeros(194)
    total_tweets = 0
    for file in glob(str(sys.argv[1])+"/*/*empath.tsv"):
        #print(file)
        with open(file, 'rU') as f:
            tsvreader = csv.reader(f, delimiter='\t') 
            tsvreader = csv.reader(f, delimiter='\t') 
            fields = next(tsvreader)[sentiment_at:]
            #194 categories
            
            for row in tsvreader:
                total_tweets += 1
                rates = np.zeros(194)
                count = 0
                for s in row[sentiment_at:]:
                    rates, count = floats_man(s, rates, count)
                totaling = totaling + rates
            
    print("Total Tweets", total_tweets)
    #print(totaling)
    track = pd.Series((totaling/float(total_tweets)), fields)
    final = track.sort_values(ascending=False)[:sentiment_at]
    print(final)
    return final

def floats_man(s, rates, count):
    try:
        rates[count] = float(s)
    except:
        rates[count] = 0.0
    count += 1
    return rates, count

#pass in tsv_format
def total_a_folder_by_category(content_at, tweet_type_at, sentiment_at, file_label):
    fields = []
    totaling = np.zeros(194)
    total_tweets = 0
    total_retweets = 0
    total_replies = 0
    total_mentions = 0
    tweet_totaling = np.zeros(194)
    reply_totaling = np.zeros(194)
    retweet_totaling = np.zeros(194)
    mention_totaling = np.zeros(194)

    for file in glob(str(sys.argv[1])+"/*/*empath.tsv"):
        #print(file)
        with open(file, 'rU') as f:
            tsvreader = csv.reader(f, delimiter='\t') 
            tsvreader = csv.reader(f, delimiter='\t') 
            fields = next(tsvreader)[sentiment_at:]
            #194 categories
            
            for row in tsvreader:
                if row[tweet_type_at] == "Tweet":
                    #print("Tweet")
                    total_tweets += 1
                    tweet_rates = np.zeros(194)
                    count = 0
                    #print(row[21:])
                    for s in row[sentiment_at:]:
                        tweet_rates, count = floats_man(s, tweet_rates, count)
                        tweet_totaling = tweet_totaling + tweet_rates
                if row[tweet_type_at] == "Reply":
                    total_replies += 1
                    reply_rates = np.zeros(194)
                    count = 0
                    for s in row[sentiment_at:]:
                        reply_rates, count = floats_man(s, reply_rates, count)
                        reply_totaling = reply_totaling + reply_rates
                if row[tweet_type_at] == "Retweet":
                    total_retweets += 1
                    retweet_rates = np.zeros(194)
                    count = 0
                    for s in row[sentiment_at:]:
                        retweet_rates, count = floats_man(s, retweet_rates, count)
                        retweet_totaling = retweet_totaling + retweet_rates
                mentions = ['@'+re.sub(r'[^\w\s]','',i) for i in ((row[content_at].replace('b\'','').replace('b\"','')).strip('\'').strip('\"')).split(" ") if "@" in i][1:]
                #print(mentions)
                if mentions != []:
                    total_mentions += 1
                    mention_rates = np.zeros(194)
                    count = 0
                    for s in row[sentiment_at:]:
                        mention_rates, count = floats_man(s, mention_rates, count)
                        mention_totaling = mention_totaling + mention_rates
            
   
    tweet_track = pd.Series((tweet_totaling/float(total_tweets)), fields)
    retweet_track = pd.Series((retweet_totaling/float(total_replies)), fields)
    reply_track = pd.Series((reply_totaling/float(total_retweets)), fields)
    mention_track = pd.Series((mention_totaling/float(total_mentions)), fields)
    tweet_final = tweet_track.sort_values(ascending=False)[:sentiment_at]
    retweet_final = retweet_track.sort_values(ascending=False)[:sentiment_at]
    reply_final = reply_track.sort_values(ascending=False)[:sentiment_at]
    mention_final = mention_track.sort_values(ascending=False)[:sentiment_at]

    tweet_final.to_pickle("./tweet_final_{}.pkl".format(file_label))
    retweet_final.to_pickle("./retweet_final_{}.pkl".format(file_label))
    reply_final.to_pickle("./reply_final_{}.pkl".format(file_label))
    mention_final.to_pickle("./mention_final_{}.pkl".format(file_label))

    print("Tweet_Final")
    print("Total Tweets", float(total_tweets))
    print(tweet_final)
    print("Retweet_Final")
    print("Total Retweets", float(total_retweets))
    print(retweet_final)
    print("Mention_Final")
    print("Total Mentions", float(total_mentions))
    print(mention_final)
    print("Reply_Final")
    print("Total Reply", float(total_replies))
    print(reply_final)


'''
To run the scandal_empath data on empath_all folder:
total_a_folder_by_category(3, 17, 20, 'scandal')
'''


'''
To run the general_empath data on empath_general folder: 
total_a_folder_by_category(3, 18, 21, 'general')
'''

'''
To run empath on the scandal data:
empath_a_folder("all", 3)
'''

'''
To run empath on the general data:
empath_a_folder("general", 3)
'''