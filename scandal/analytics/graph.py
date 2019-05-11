from empath import Empath
import csv 
from glob import glob
import sys
import os
import numpy as np
import pandas as pd

#Every edge knows its original poster user and its repost destination user
#The reposts and the number fo comments will influence the weight of the edge
class edge:
    def __init__(self, origin_user, repost_user, comment_user):
        self.origin = origin_user
        self.repost = repost_user
        self.comments = comment_user
        self.weight = 0

class user_node: 
    def __init__(self, author, name, location):
        self.author = author
        self.name = name 
        self.location = location

        self.my_tweets = []
        self.my_edges = []
        self.num_tweets = 0
        self.num_retweets = 0
        self.num_replies = 0 

    def update_info(self, tweet):
        if tweet.kind == "Tweet":
            self.num_tweets += 1
            self.my_tweets.append(tweet)
        if tweet.kind == "Reply":
            self.num_replies += 1
        if tweet.kind == "Retweet":
            self.num_retweets += 1



class tweet:
    def __init__(self, kind, sentiment, content):
        self.kind = kind
        self.sentiment = sentiment
        self.content = content

#A function to normalize the edge weights between 0-1
def normalize(edge):
    return None

#We need to find out seeds to begin the graph
#Maybe start with the post prolific posters
def get_seeds():
    return None

#Go through all the tweets in the dataset and create nodes for all users
#Tweets can be "Tweet", "Reply", "Retweet" in column 17
def create_user_nodes():
    users = {}
    for file in glob(str(sys.argv[1])+"/*.tsv"):
        with open(file, 'rU') as f:
            tsvreader = csv.reader(f, delimiter='\t') 
            fields = next(tsvreader)
            for row in tsvreader: 
                sentiment = get_sentiment(fields, row)
                new_tweet = tweet(row[17], sentiment, row[3])
                
                #If the user has been created already
                #Increment the number of tweets
                if row[4] in users:
                    cur_user = users[row[4]]
                    cur_user.update_info(new_tweet)

                else:
                    #Setting the location is not going to be as easy as this in actuality
                    new_user = user_node(row[4], row[5], (row[6]+" "+row[7]+" "+row[8]))
                    new_user.update_info(new_tweet)
                    #print(new_user.name)
                    users[row[4]] = new_user
                    print(users[row[4]])
    return users

def create_edges():
    return None

def get_sentiment(fields, row):
    sentiment = {}
    count = 20
    for s in row[20:]:
        if float(s) > 0:
            sentiment[fields[count]] = float(s)
            count += 1
    return sentiment 

def print_users(users):
    for user in users.values():
        print("Name: ", user.name)
        print("    Location: ", user.location)
        print("    Tweets: ", user.num_tweets)

users = create_user_nodes()
print_users(users)
                    


                
    








