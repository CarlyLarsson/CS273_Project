'''We want to create charts for the top twenty 
   empath results and compare them to normal users'''

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from analytics.sentiment_analysis import totaling_a_folder
import math
import sys


def get_sentiment_data(path, top_num):
    top = pd.read_pickle(path)[:top_num]
    labels = []
    freqs = []
    for label in top.index:
        labels.append(label)
        freqs.append(top[label])
    return labels, freqs

def get_general_sentiment_data_matcher(gen_path, scandal_labels):
    general_df = pd.read_pickle(gen_path)
    gen_labels = []
    gen_freqs = []
    for label in scandal_labels:
        freq = general_df[label]
        gen_labels.append(label)
        gen_freqs.append(freq)
    return gen_labels, gen_freqs

def plot_college_scandal_comp(scandal_labels, scandal_freq, 
                         general_labels, general_freq,
                         tweet_type):
    ind = np.arange(len(scandal_freq))  # the x locations for the groups
    width = 0.35  # the width of the bars
    assert scandal_labels == general_labels

    fig, ax = plt.subplots()

    plot_scandal = []
    plot_general = []
    for n in scandal_freq:
        plot_scandal.append(math.ceil(n))

    for n in general_freq:
        plot_general.append(math.ceil(n))

    rects1 = ax.bar(ind - width/2, plot_scandal, width,
                    label='{} About the College Scandal'.format(tweet_type))
    rects2 = ax.bar(ind + width/2, plot_general, width,
                    label='{} From Average Users'.format(tweet_type))

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Frequency of Occurance')
    ax.set_title('Top 10 Sentiment Keywords from College Scandal')
    ax.set_xticks(ind)
    ax.set_xticklabels(scandal_labels, rotation='vertical')
    ax.legend()
    
    fig.tight_layout()
    plt.savefig('graph_comp_{}.png'.format(tweet_type))
    #plt.show()

def plot_college_scandal_tops(labels, freq, tweet_type, ds, color):
    ind = np.arange(len(freq))  # the x locations for the groups
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()

    plot = []

    for n in freq:
        plot.append(math.ceil(n))

    rects1 = ax.bar(ind - width/2, plot, width,
                    label='Top {} From {}'.format(tweet_type, ds.title()),
                    color=color)

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Frequency of Occurance')
    ax.set_title('Sentiment Keywords')
    ax.set_xticks(ind)
    ax.set_xticklabels(labels, rotation='vertical')
    ax.legend()
    
    fig.tight_layout()
    plt.savefig('graph_top_{}_{}.png'.format(ds, tweet_type))
    #plt.show()


def top_tens_graph():
    pkl_list = [
        ["mention_final_scandal.pkl", "mention_final_general.pkl"], 
        ["tweet_final_scandal.pkl", "tweet_final_general.pkl"]
    ]
    for comp in pkl_list:
        path_scandal = str(sys.argv[1]) + comp[0]
        path_gen = str(sys.argv[1]) + comp[1]
        tweet_type = (comp[0].split("_")[0]+"s").title()
        
        scandal_labels, scandal_freq = get_sentiment_data(path_scandal, 10)
        plot_college_scandal_tops(scandal_labels, scandal_freq, tweet_type, 'scandal', 'C0')
        gen_labels, gen_freq = get_sentiment_data(path_gen, 10)
        plot_college_scandal_tops(gen_labels, gen_freq, tweet_type, 'general', 'C1')


def compare_graphs():
    pkl_list = [
        ["mention_final_scandal.pkl", "mention_final_general.pkl"], 
        ["retweet_final_scandal.pkl", "retweet_final_general.pkl"],
        ["reply_final_scandal.pkl", "reply_final_general.pkl"],
        ["tweet_final_scandal.pkl", "tweet_final_general.pkl"]
    ]
    
    for comp in pkl_list:
        path_scandal = str(sys.argv[1]) + comp[0]
        path_gen = str(sys.argv[1]) + comp[1]
        tweet_type = (comp[0].split("_")[0]+"s").title()
        scandal_labels, scandal_freq = get_scandal_sentiment_data(path_scandal, 10)
        general_labels, general_freq = get_sentiment_data_matcher(path_gen, scandal_labels)
        plot_college_scandal_comp(scandal_labels, scandal_freq, 
                             general_labels, general_freq,
                             tweet_type)


top_tens_graph()

'''
/Users/carlylarsson/Documents/CS273/CS273_Project/scandal/analytics/pkl_df
'''