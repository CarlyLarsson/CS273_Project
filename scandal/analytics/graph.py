from empath import Empath
import csv 
from glob import glob
import sys
import os
import numpy as np
import pandas as pd
import re
from py2neo import Graph, Node, Relationship, NodeMatcher
from datetime import datetime
# from py2neo.data import Node, Relationship


uri = "bolt://localhost:7687"
user = "neo4j"
password = "spring2019"

graph = Graph(uri=uri, user=user, password=password)
matcher = NodeMatcher(graph)
# optionally clear the graph
graph.delete_all()

# print(len(g.nodes))
# print(len(g.relationships))

#https://py2neo.org/2.0/intro.html
#Every edge knows its original poster user and its repost destination user
#The reposts and the number fo comments will influence the weight of the edge
# class edge:
#     def __init__(self, from_user, to_user):
#         self.from_user = origin_user
#         self.to_user = repost_user
#         self.weight = 0

#For every tweet there is an edge:
    #For a original tweet it is a loop back to the author
    #For a retweet it is an edge from the reposter to the original author
    #For a reply it would be an edge from the author of the reply to the author of the originl post

class user_node: 
    def __init__(self, author, name, location):
        self.author = author
        self.name = name 
        self.location = location

        self.latitude = 0
        self.longitude = 0

        self.my_tweets = []
        self.my_replies = []
        self.my_retweets = []
        self.my_potential_mentions = []

        self.outgoing = 0
        self.incoming = 0
        self.num_tweets = 0
        self.num_retweets = 0
        self.num_replies = 0 
        self.num_mentions = 0

    def update_info(self, tweet):
        if tweet != None:
            if tweet.kind == "Tweet":
                self.num_tweets += 1
                self.my_tweets.append(tweet)
                self.my_potential_mentions.append(tweet)
            if tweet.kind == "Reply":
                self.num_replies += 1
                self.my_replies.append(tweet)
                self.my_potential_mentions.append(tweet)
            if tweet.kind == "Retweet":
                self.num_retweets += 1
                self.my_retweets.append(tweet)

class tweet:
    def __init__(self, kind, sentiment, content, dt):
        self.kind = kind
        self.sentiment = sentiment
        self.content = content
        self.dt = dt

#A function to normalize the edge weights between 0-1
def normalize(edge):
    return None

#Go through all the tweets in the dataset and create nodes for all users
#Tweets can be "Tweet", "Reply", "Retweet" in column 17
def create_user_nodes():
    users = {}
    for file in glob(str(sys.argv[1])+"/*/*.tsv"):
        print(file)
        with open(file, 'rU') as f:
            tsvreader = csv.reader(f, delimiter='\t') 
            fields = next(tsvreader)
            for row in tsvreader: 
                sentiment = get_sentiment(fields, row)
                dt = datetime.strptime(row[1], '%Y-%m-%d %X')
                new_tweet = tweet(row[17], sentiment, row[3], dt)
                
                #If the user has been created already
                #Increment the number of tweets
                if row[4] in users:
                    cur_user = users[row[4]]
                    cur_user.update_info(new_tweet)

                else:
                    #Setting the location is not going to be as easy as this in actuality
                    #author, name, location
                    new_user = user_node(row[4], row[5], (row[8]+","+row[7]+","+row[6]))
                    new_user.update_info(new_tweet)
                    #print(new_user.name)
                    users[row[4]] = new_user
    return users


#Graph stuff
def create_user_node_in_graph(users):
    #graph.delete_all()
    #https://stackoverflow.com/questions/51796919/py2neo-cannot-create-graph
    # https://py2neo.org/2.0/essentials.html#py2neo.Graph.create
    for user in users.values():  
        user_node_in_graph = Node("User", 
                                        author=user.author,
                                        name=user.name, 
                                        location=user.location, 
                                        orig_tweet_count=user.num_tweets,
                                        retweet_count=user.num_retweets,
                                        reply_count=user.num_replies,
                                        mention_count=user.num_mentions)
        graph.create(user_node_in_graph)
        # tx.commit()
    return (len(graph.nodes))


def node_exists_in_graph(lbl, username):
    matcher = NodeMatcher(graph)
    # matcher.match("Person", name="Keanu Reeves").first()
    m = matcher.match(lbl, author = username).first()
    if m is None:
        return None
    else:
        # print(m)
        return m

def find_node_csv(author):
    for user in users.values():
        if user.author == author:
            return user
    return None

def create_single_csv_node(author, tweet):
    new_user = user_node(author, None, None)
    new_user.update_info(tweet)
    return new_user

def create_retweet_relations(users):
    for user in users.values():
        if user.num_retweets > 0: 
            for retweet in user.my_retweets:
                #Get name of original author 
                sp_tweet = ((retweet.content.replace('b\'','').replace('b\"','')).strip('\'').strip('\"')).split()
                author = sp_tweet[1]
                author_node = find_node_csv(author)
                

                if author_node == None:
                    new_tweet = tweet("Tweet", retweet.sentiment, retweet.content, retweet.dt)
                    author_node = create_single_csv_node(author, new_tweet)

                userB = node_exists_in_graph("User", author_node.author) 
                userA = node_exists_in_graph("User", user.author)

                if userB == None:
                    user_node_in_graph = Node("User", 
                                    author=author,
                                    name='', 
                                    location='', 
                                    orig_tweet_count=0,
                                    retweet_count=1,
                                    reply_count=0,
                                    mention_count=0)

                    graph.create(user_node_in_graph)
                    userB = node_exists_in_graph("User", author_node.author)
                print("creating retweet relationship")
                dt = retweet.dt.strftime("%F")
                time = retweet.dt.strftime("%s")
                userA_retweets_userB = Relationship(userA, "RETWEETED", userB, timestamp=time, date=dt)
                graph.create(userA_retweets_userB)

def create_reply_relations(users):
    for user in users.values():
        for reply in user.my_replies:
            replied_to_user = ((reply.content.replace('b\'','').replace('b\"','')).strip('\'').strip('\"')).split(" ")[0]
            #want to replace those with a period
            if "." in replied_to_user:
                replied_to_user.replace(".","")
            #if replied_to_user not in database, add the user
            if node_exists_in_graph('User', replied_to_user) == None:
                user_node_in_graph = Node("User", 
                                    author=replied_to_user,
                                    name='', 
                                    location='', 
                                    orig_tweet_count=0,
                                    retweet_count=0,
                                    reply_count=0,
                                    mention_count=0)

                graph.create(user_node_in_graph)

            #if replied_to_user is not in csv original list, add user
            if replied_to_user not in users:
                new_tweet = tweet(None, None, None, None)
                create_single_csv_node(replied_to_user,new_tweet)          
            
            print("creating reply relationship")
            dt = reply.dt.strftime("%F")
            time = reply.dt.strftime("%s")
            userA_replied_to_userB = Relationship(node_exists_in_graph('User', user.author), "REPLIED_TO", node_exists_in_graph('User', replied_to_user), timestamp=time, date=dt)
            graph.create(userA_replied_to_userB)

def create_mention_relations(users):
    for user in users.values():
        for tweet_ in user.my_potential_mentions:
            mentions = ['@'+re.sub(r'[^\w\s]','',i) for i in ((tweet_.content.replace('b\'','').replace('b\"','')).strip('\'').strip('\"')).split(" ") if "@" in i][1:]
            # print(mentions)
            # #want to replace those with a period
            # if "." in replied_to_user:
            #     replied_to_user.replace(".","")
            #if replied_to_user not in database, add the user

            #if replied_to_user is not in csv original list, add user
            for mention in mentions:
                if mention not in users:
                    new_tweet = tweet(None, None, None, None)
                    new_node = create_single_csv_node(mention, new_tweet)  
                    new_node.num_mentions += 1

                if node_exists_in_graph('User', mention) != None:
                    old_node = node_exists_in_graph('User', mention)
                    print(old_node)
                    old_node["mention_count"] += 1
                    graph.push(old_node)
                else:
                    user_node_in_graph = Node("User", 
                                        author=mention,
                                        name='', 
                                        location='', 
                                        orig_tweet_count=0,
                                        retweet_count=0,
                                        reply_count=0,
                                        mention_count=1)

                    graph.create(user_node_in_graph)
                
                


                print("creating mention relationship")
                dt = mention.dt.strftime("%F")
                time = mention.dt.strftime("%s")
                userA_mentioned_userB = Relationship(node_exists_in_graph('User', user.author) , "MENTIONED", node_exists_in_graph('User', mention), timestamp=time, date=dt)
                graph.create(userA_mentioned_userB)


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
        print_tweets(user.my_tweets)

def print_tweets(tweets):
    for tweet in tweets:
        print("    Tweet: ", tweet.content)
        print("    Sentiment: ", tweet.sentiment)

users = create_user_nodes()
create_user_node_in_graph(users)
create_reply_relations(users)
create_retweet_relations(users)
create_mention_relations(users)





