'''We want to create charts for the top twenty 
   empath results and compare them to normal users'''

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from analytics.sentiment_analysis import totaling_a_folder
import math


def get_sentiment_data():
    top = totaling_a_folder()
    labels = []
    freqs = []
    for label in top.index:
        labels.append(label)
        freqs.append(top[label])
    return labels, freqs


def plot_college_scandal(labels, freq):
    ind = np.arange(len(freq))  # the x locations for the groups
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()

    plot = []
    for n in freq:
        plot.append(math.ceil(n*100))

    rects1 = ax.bar(ind - width/2, plot, width,
                    label='Tweets About the College Scandal')
    rects2 = ax.bar(ind + width/2, plot, width,
                    label='Tweets From Average Users')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Frequency of Occurance in %')
    ax.set_title('Top 20 Sentiment Keywords')
    ax.set_xticks(ind)
    ax.set_xticklabels(labels, rotation='vertical')
    ax.legend()
    
    fig.tight_layout()
    plt.show()
    
labels, freq = get_sentiment_data()
plot_college_scandal(labels, freq)