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
    for folder in glob(str(sys.argv[1])+"/*"):
        # print(os.path.splitext(os.path.basename(folder))[0])
        print(os.getcwd())
        cwd = os.getcwd()
        empath_folder = cwd + "/empath/" + os.path.splitext(os.path.basename(folder))[0] + "/"
        os.makedirs(empath_folder)
        for file in glob(folder+"/*.tsv"):
            file_name = (os.path.splitext(os.path.basename(file))[0])
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
    totaling = np.zeros(194)
    total_tweets = 0
    for file in glob(str(sys.argv[1])+"/*empath.tsv"):
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
    final = track.sort_values(ascending=False)[:50]
    print(final)
    return final


empath_a_folder()