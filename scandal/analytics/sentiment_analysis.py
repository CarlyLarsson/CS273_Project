from empath import Empath
import csv 
from glob import glob
import sys
import os
import numpy as np
import pandas as pd

def sent_analyze(tweet):
    lexicon = Empath()
    sent = lexicon.analyze(tweet, normalize=False)
    return sent

def empath_a_folder():
    #print(sys.argv[1])
    for folder in glob(str(sys.argv[1])+"/*"):
        # print(os.path.splitext(os.path.basename(folder))[0])
        print(os.getcwd())
        cwd = os.getcwd()
        empath_folder = cwd + "/empath_all/" + os.path.splitext(os.path.basename(folder))[0] + "/"
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
                    tweet = row[3]
                    empath_reading = sent_analyze(tweet)
                    for result in empath_reading.values():
                        row.append(result)
                    tsvwriter.writerow(row)

def totaling_a_folder():
    #Go through all the given tweets empath results and return the top 10 category scoreres
    fields = []
    totaling = np.zeros(194)
    total_tweets = 0
    for file in glob(str(sys.argv[1])+"/*/*empath.tsv"):
        with open(file, 'rU') as f:
            tsvreader = csv.reader(f, delimiter='\t') 
            tsvreader = csv.reader(f, delimiter='\t') 
            fields = next(tsvreader)[20:]
            #194 categories
            
            for row in tsvreader:
                total_tweets += 1
                rates = np.zeros(194)
                count = 0
                for s in row[20:]:
                    rates[count] = float(s)
                    count += 1
                totaling = totaling + rates
            
    print(total_tweets)
    track = pd.Series((totaling/float(total_tweets)), fields)
    final = track.sort_values(ascending=False)[:20]
    #print(final)
    return final

def total_a_folder_by_category():
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
        with open(file, 'rU') as f:
            tsvreader = csv.reader(f, delimiter='\t') 
            tsvreader = csv.reader(f, delimiter='\t') 
            fields = next(tsvreader)[20:]
            #194 categories
            
            for row in tsvreader:
                print(row[19])
                if row[17] == "Tweet":
                    print("Tweet")
                    total_tweets += 1
                    tweet_rates = np.zeros(194)
                    count = 0
                    for s in row[20:]:
                        tweet_rates[count] = float(s)
                        count += 1
                        tweet_totaling = tweet_totaling + tweet_rates
                if row[19] == "Reply":
                    total_replies += 1
                    reply_rates = np.zeros(194)
                    count = 0
                    for s in row[20:]:
                        reply_rates[count] = float(s)
                        count += 1
                        reply_totaling = reply_totaling + reply_rates
                if row[19] == "Retweet":
                    total_retweets += 1
                    retweet_rates = np.zeros(194)
                    count = 0
                    for s in row[20:]:
                        retweet_rates[count] = float(s)
                        count += 1
                        retweet_totaling = retweet_totaling + retweet_rates
                mentions = ['@'+re.sub(r'[^\w\s]','',i) for i in ((row[3].replace('b\'','').replace('b\"','')).strip('\'').strip('\"')).split(" ") if "@" in i][1:]
                #print(mentions)
                if mentions != []:
                    total_mentions += 1
                    mention_rates = np.zeros(194)
                    count = 0
                    for s in row[20:]:
                        print("Row", row[20])
                        mention_rates[count] = float(s)
                        count += 1
                        mention_totaling = mention_totaling + mention_rates
            
    print(tweet_totaling)
    tweet_track = pd.Series((tweet_totaling/float(total_tweets)), fields)
    retweet_track = pd.Series((retweet_totaling/float(total_replies)), fields)
    reply_track = pd.Series((reply_totaling/float(total_retweets)), fields)
    mention_track = pd.Series((mention_totaling/float(total_mentions)), fields)
    tweet_final = tweet_track.sort_values(ascending=False)[:20]
    retweet_final = retweet_track.sort_values(ascending=False)[:20]
    reply_final = reply_track.sort_values(ascending=False)[:20]
    mention_final = mention_track.sort_values(ascending=False)[:20]

    print("Tweet_Final")
    print(tweet_final)
    print("Retweet_Final")
    print(retweet_final)
    print("Mention_Final")
    print(mention_final)
    print("Reply_Final")
    print(reply_final)
    return final

empath_a_folder()