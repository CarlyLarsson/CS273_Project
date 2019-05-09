from empath import Empath
import csv 
from glob import glob
import sys
import os

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

get_tweets()
