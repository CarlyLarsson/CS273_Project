from empath import Empath
import csv 
from glob import glob
import sys
import os
import numpy as np
import pandas as pd

def sent_analyze(tweet):
    lexicon = Empath()
    sent = lexicon.analyze(tweet, normalize=True)
    return sent

def get_tweets():
    for file in glob(str(sys.argv[1])+"/*.tsv"):
        with open(file, 'rU') as f, open(os.path.basename(file)[0:-4]+"_empath.tsv", 'w') as nf:
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

def totaling():
    #Go through all the given tweets empath results and return the top 10 category scoreres
    for file in glob(str(sys.argv[1])+"/*empath.tsv"):
        with open(file, 'rU') as f:
            tsvreader = csv.reader(f, delimiter='\t') 
            tsvreader = csv.reader(f, delimiter='\t') 
            fields = next(tsvreader)[20:]
            #194 categories
            totaling = np.zeros(194)

            for row in tsvreader:
                rates = np.zeros(194)
                count = 0
                for s in row[20:]:
                    rates[count] = float(s)
                    count += 1
                totaling = totaling + rates

            track = pd.Series(totaling, fields)
            return track.sort_values(ascending=False)[:20]
