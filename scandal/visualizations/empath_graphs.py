'''We want to create charts for the top twenty 
   empath results and compare them to normal users'''

import numpy as np
import matplotlib.pyplot as plt
from analytics.graph.sentiment_analysis import totaling_a_folder

def get_sentiment_data():
    #Run on 
    top = totaling_a_folder()


def plot_all():
    # width of the bars
    barWidth = 0.3
    
    # Choose the height of the blue bars
    bars1 = [10, 9, 2]
    
    # Choose the height of the cyan bars
    bars2 = [10.8, 9.5, 4.5]
    
    # The x position of bars
    r1 = np.arange(len(bars1))
    r2 = [x + barWidth for x in r1]
    
    # Create blue bars
    plt.bar(r1, bars1, width = barWidth, color = 'blue', edgecolor = 'black', yerr=yer1, capsize=7, label='poacee')
    
    # Create cyan bars
    plt.bar(r2, bars2, width = barWidth, color = 'cyan', edgecolor = 'black', yerr=yer2, capsize=7, label='sorgho')
    
    # general layout
    plt.xticks([r + barWidth for r in range(len(bars1))], ['cond_A', 'cond_B', 'cond_C'])
    plt.ylabel('height')
    plt.legend()
    
    # Show graphic
    plt.show()


plot_all()