import sys
import csv
from graph import *
import requests
import json
import time
import pandas as pd
import matplotlib as mpl
mpl.use('agg')
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import calendar
from glob import glob
import sys
import numpy as np
import pickle
import re
from py2neo import Graph, Node, Relationship, NodeMatcher
from datetime import datetime
from dateutil.relativedelta import relativedelta
# from py2neo.data import Node, Relationship
from tqdm import tqdm
import dill
import matplotlib.animation
# plt.rcParams['animation.ffmpeg_path'] = '/usr/bin/ffmpeg'


#https://python-graph-gallery.com/300-draw-a-connection-line/
#https://python-graph-gallery.com/315-a-world-map-of-surf-tweets/

def merge_capital_to_US_data():
    with open("uscitiesv1.5.csv","r") as inputWholeUSData, open("capitals_US.csv","r") as inputCapitals, open("uscitiesv1.5_with_capitals.csv","w") as output:
        reader1 = csv.reader(inputWholeUSData)
        reader2 = csv.reader(inputCapitals)
        writer = csv.writer(output)
        header1 = next(reader1,)
        header2 = next(reader2,)
        header1.append("capital")
        writer.writerow(header1)
        capitals = [str(row[1])+","+str(row[0]) for row in reader2]
        for row in reader1:
            if str(row[0])+","+str(row[3]) in capitals:
                row.append('True')
            writer.writerow(row)            
         
def get_US_location():
    users = create_user_nodes()
    total_users_location = []
    # print(users)
    #https://locationiq.com/docs#forward-geocoding
    not_US_city = []
    not_US_no_city = []
    in_US_city = []
    in_US_no_city = []

    with open("hashtags_map_data.csv","r") as inputData:
        reader = csv.reader(inputData)
        map_data = [row for row in reader]
        user_exist = [row[0] for row in map_data]
        input_map_data = {row[1]: row for row in map_data}

    for user in users.values():
        if user.author in user_exist:
            continue
        location_list = (user.location).split(",")
        if (location_list[2] != '' and location_list[1] != ''):
            # print(location_list)
            if location_list[2] != "United States of America":
                if location_list[0] != '':
                    not_US_city.append([user.author,user.location])
                else:
                    not_US_no_city.append([user.author,user.location])
            else:
                if location_list[0] != '':
                    in_US_city.append([user.author,user.location])
                else:
                    in_US_no_city.append([user.author,user.location])
    print(not_US_city)
    #if has city and in the United States get long and lat
    count_total_city = 0
    # with open("uscitiesv1.5.csv", "r") as inputMapData, open("hashtags_map_data.csv", "w") as outputUSMapData:
    
    print("doing this")
    with open("uscitiesv1.5.csv", "r") as inputMapData,open("hashtags_map_data.csv", "a") as outputUSMapData:        
        writer = csv.writer(outputUSMapData)
        reader = csv.reader(inputMapData)
        header = next(reader,)
        map_data = [row for row in reader]
        US_dict = {str(row[0])+","+str(row[3])+",United States of America" : str(row[6])+","+str(row[7]) for row in map_data}
        # print(US_dict)
        US_capital = {","+str(row[3])+",United States of America" : str(row[6])+","+str(row[7]) for row in map_data if row[-1] != None}
        for user_location in in_US_city:
            count_total_city +=1
            if str(user_location[1]) in US_dict:
                lat_lng = (US_dict[str(user_location[1])]).split(",")
                user_location.append(lat_lng[0])
                user_location.append(lat_lng[1])
                writer.writerow(user_location)
        # print(US_capital)
        for user_location in in_US_no_city:
            if str(user_location[1]) in US_capital:
                lat_lng = (US_capital[str(user_location[1])]).split(",")
                user_location.append(lat_lng[0])
                user_location.append(lat_lng[1])
                writer.writerow(user_location)
                print(user_location)

    return in_US_city, in_US_no_city, not_US_city, not_US_no_city
#merge back user to user data maybe to put in nodes
# def merge_back_user():

def get_location_not_US(not_US_city_list,not_US_no_city_list):
    url = "https://us1.locationiq.com/v1/search.php"
    fetch_again = []
    with open("hashtags_map_data.csv","r") as inputData:
        reader = csv.reader(inputData)
        map_data = [row for row in reader]
        user_exist = [row[0] for row in map_data]
        input_map_data = {row[1]: row for row in map_data}

    for user_location in not_US_city_list:
        if user_location[0] in user_exist:
            print("user exists")
            continue
        #remove first comma from string
        location_query = (user_location[1])
        if location_query == "Washington, D.C.,District of Columbia,United States of America":
            print("DC exists")
            user_location.append(input_map_data["Washington D.C.,District of Columbia,United States of America"][2])
            user_location.append(input_map_data["Washington D.C.,District of Columbia,United States of America"][3])
    
        if location_query in input_map_data:                
            user_location.append(input_map_data[location_query][2])
            user_location.append(input_map_data[location_query][3])
        else:
            print(location_query)
            data = {
                'key': '76223a178f328b',
                'q': location_query,
                'format': 'json'
            }
            try:
                time.sleep(2)
                response = requests.get(url, params=data)
                response_json = response.json()
                print(response_json)
                with open("locationIQ_json_dump.json","a") as outputJSON:
                    json.dump(response_json,outputJSON)
                    outputJSON.write("\n")
                
                user_lat = response_json[0]["lat"]
                user_lon = response_json[0]["lon"]
                user_location.append(user_lat)
                user_location.append(user_lon)
                
            except Exception as e:
                print(str(e))

                time.sleep(5)
                continue
        with open("hashtags_map_data.csv", "a") as outputUSMapData:
            writer = csv.writer(outputUSMapData)
            writer.writerow(user_location)

    for user_location in not_US_no_city_list:
        #remove first comma from string
        if user_location[0] in user_exist:
            print("user exists")
            continue
        location_query = (user_location[1][1:])
        if user_location[1] in input_map_data:
            user_location.append(input_map_data[user_location[1]][2])
            user_location.append(input_map_data[user_location[1]][3])
        else:
            print(location_query)
            data = {
                'key': '76223a178f328b',
                'q': location_query,
                'format': 'json'
            }
            try:
                time.sleep(2)
                response = requests.get(url, params=data)
                response_json = response.json()
                print(response_json)
                with open("locationIQ_json_dump.json","a") as outputJSON:
                    json.dump(response_json,outputJSON)
                    outputJSON.write("\n")
                
                user_lat = response_json[0]["lat"]
                user_lon = response_json[0]["lon"]
                user_location.append(user_lat)
                user_location.append(user_lon)
                
            except Exception as e:
                print(str(e))
                # fetch_again.append(user_location)
                time.sleep(5)
                continue

        with open("hashtags_map_data.csv", "a") as outputUSMapData:
            writer = csv.writer(outputUSMapData)
            writer.writerow(user_location)
    
    return not_US_city_list, not_US_no_city_list


# replied_to_user = ((reply.content.replace('b\'','').replace('b\"','')).strip('\'').strip('\"')).split(" ")[0]
def get_different_times():
    users = create_user_nodes()
    # pd.DataFrame([])
    users_time = []

    for user in users.values():
        for tweet_ in user.my_original_tweets:
            # tweet_strip = ((tweet_.content.replace('b\'','').replace('b\"','')).strip('\'').strip('\"')).split(" ")[0]
            first_day = datetime.strptime("2019-03-12 00:00:00", '%Y-%m-%d %X')
            one_day = datetime.strptime("2019-03-13 00:00:00", '%Y-%m-%d %X')
            date_after_three_days = first_day + relativedelta(days=+3)
            date_after_week = first_day + relativedelta(weeks=+1)
            date_after_month = first_day + relativedelta(months=+1)
            if tweet_.dt == "": continue
            if tweet_.dt < one_day:
                users_time.append([user.author,1])
            if tweet_.dt < date_after_three_days:
                users_time.append([user.author,3])
            if tweet_.dt < date_after_week:
                users_time.append([user.author,7])
            if tweet_.dt < date_after_week:
                users_time.append([user.author,30])
            users_time.append([user.author,60])
    return users_time
def get_every_day(all_data,dataframe_):
# def get_every_day():
    # users = create_user_nodes()
    # pd.DataFrame([])
    # data = pd.read_csv('hashtags_map_data.csv', sep=",")
    # users_time = []
    data = dataframe_
    data["Date"] = np.nan
    print("putting into pandas")
    for user in tqdm(users.values()):
        for tweet_ in user.my_original_tweets:
            # tweet_strip = ((tweet_.content.replace('b\'','').replace('b\"','')).strip('\'').strip('\"')).split(" ")[0]
            data.loc[data["author"] == user.author, ["Date"]] = tweet_.dt

    data['Date']=pd.to_datetime(data['Date'])
    data.sort_values(by=['Date'])
    pickle.dump( data, open( "dates_added_data_replies2.p", "wb" ) )

    print("getting everyday now")
    first_day = datetime.strptime("2019-03-13 00:00:00", '%Y-%m-%d %X')
    last_day = datetime.strptime("2019-05-13 00:00:00", '%Y-%m-%d %X')
    count = 1
    while first_day < last_day:
        new_data = data
        new_data2 = all_data
        new_data = data.drop(data[data.Date > first_day].index)
        new_data2 = all_data.drop(all_data[all_data.Date > first_day].index)
        create_map(new_data2,new_data, ("day_%d" % count),count)
        # create_map(new_data, ("day_%d" % count),count)
        print("finished day: %d" % count)
        count= count + 1
        first_day = first_day + relativedelta(days=+1)
  
    



def create_data_frame_for_map(user_time_list):
    print("creating data frames")
     # read the data (on the web)
    data = pd.read_csv('hashtags_map_data.csv', sep=",")
    # n = data["location"].value_counts()
    data["one_day"] = 0
    data["three_day"] = 0
    data["one_week"] = 0
    data["one_month"] = 0
    data["two_month"] = 0


    for user in tqdm(user_time_list):
        if user[1] == 1:
            data.loc[data["author"] == user[0], ["one_day"]] = 1
        if user[1] == 3:
            data.loc[data["author"] == user[0], ["three_day"]] = 1
        if user[1] == 7:
            data.loc[data["author"] == user[0], ["one_week"]] = 1
        if user[1] == 30:
            data.loc[data["author"] == user[0], ["one_month"]] = 1
        if user[1] == 60:
            data.loc[data["author"] == user[0], ["two_month"]] = 1
        
        
    new = data['location'].str.split(",", n = 2, expand = True)
    data["country"] = new[2]

    one_day_data =  data.loc[data['one_day'] == 1]
    pickle.dump( one_day_data, open( "one_day_data.p", "wb" ) )
    
    three_day_data =  data.loc[data['three_day'] == 1]
    pickle.dump( three_day_data, open( "three_day_data.p", "wb" ) )

    week_day_data =  data.loc[data['one_week'] == 1]
    pickle.dump( week_day_data, open( "week_day_data.p", "wb" ) )

    month_day_data =  data.loc[data['one_month'] == 1]
    pickle.dump( month_day_data, open( "month_day_data.p", "wb" ) )

    month2_day_data =  data.loc[data['two_month'] == 1]
    pickle.dump( month2_day_data, open( "month2_day_data.p", "wb" ) )

    pickle.dump( data, open( "data.p", "wb" ) )



    return one_day_data,three_day_data,week_day_data,month_day_data,month2_day_data,data


def create_map(original_dataframe,relations_dataframe_,map_name,day_num):
# def create_map(original_dataframe,map_name,day_num):
    print("Creating map")
    # with open("test_map_data.csv","r") as inputMap:
        # reader = csv.reader(inputMap)
        # for row in reader:
            
        # Set the dimension of the figure
    my_dpi=96
    plt.figure(figsize=(2600/my_dpi, 1800/my_dpi), dpi=my_dpi)
    
    data = original_dataframe
    data2 = relations_dataframe_
    # data2= data2[data2['lon2'] != 0]
    # data2= data2[data2['lat2'] != 0]
    # making separate last name column from new data frame 
    # data["Last Name"]= new[1] 
  
    # Make the background map
    m=Basemap(llcrnrlon=-180, llcrnrlat=-65,urcrnrlon=180,urcrnrlat=80)
    # m = Basemap(llcrnrlon=-119,llcrnrlat=22,urcrnrlon=-64,urcrnrlat=49,
    #     projection='lcc',lat_1=33,lat_2=45,lon_0=-95)
    m.drawmapboundary(fill_color='#A6CAE0', linewidth=0)
    m.fillcontinents(color='grey', alpha=0.3)
    m.drawcoastlines(linewidth=0.1, color="white")
    
    # prepare a color for each point depending on the continent.
    # data['labels_enc'] = pd.factorize(data['country'])[0]
    

    # print(data)
    # Add a point per position
    #doing one day
    print("plotting days")
    m.scatter(data['lon'], data['lat'], s=data["location"].value_counts()/3, alpha=1,color="blue")
    m.scatter(data2['lon2'], data2['lat2'], s=data["location"].value_counts()/3, alpha=1,color="red")
    # copyright and source data info
    plt.text( -170, -58,'College Admissions Scandal Day: %d ' % day_num, ha='left', va='bottom', size=30, color='#555555' )
    # Save as png
    plt.savefig("maps_replies2/"+str(map_name)+'.png', bbox_inches='tight')
    return

def get_replies_data() :
    print("getting replies for data")
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "spring2019"
    #https://py2neo.org/v3/database.html
    graph = Graph(uri=uri, user=user, password=password)
    matcher = NodeMatcher(graph)
    dict_relations = graph.run('MATCH (n:User)-[r:REPLIED_TO]-(m:User) \
            RETURN n.author,r,m.author').data()
    # dill.dump( dict_relations.to_json(), open( "dict_relations_reply.p", "wb" ) )

    return dict_relations

def get_retweet_data() :
    print("getting retweets for data")
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "spring2019"
    #https://py2neo.org/v3/database.html
    graph = Graph(uri=uri, user=user, password=password)
    matcher = NodeMatcher(graph)
    dict_relations = graph.run('MATCH (n:User)-[r:RETWEETED]-(m:User) \
            RETURN n.author,r,m.author').data()
    # dill.dump( dict_relations.to_json(), open( "dict_relations_reply.p", "wb" ) )

    return dict_relations

def get_mention_data() :
    print("getting mentions for data")
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "spring2019"
    #https://py2neo.org/v3/database.html
    graph = Graph(uri=uri, user=user, password=password)
    matcher = NodeMatcher(graph)
    dict_relations = graph.run('MATCH (n:User)-[r:MENTIONED]-(m:User) \
            RETURN n.author,r,m.author').data()
    # dill.dump( dict_relations.to_json(), open( "dict_relations_reply.p", "wb" ) )

    return dict_relations

def draw_lines_map(relations_dict, dataframe_,map_name):
    print("Creating map")
    
    # Set the dimension of the figure
    my_dpi=96
    fig = plt.figure(figsize=(2600/my_dpi, 1800/my_dpi), dpi=my_dpi)
    
    data = dataframe_
    # data["retweeted"] = 0
    data["lat2"] = np.nan
    data["lon2"] = np.nan
    for user in tqdm(relations_dict):
        # print(data.loc[data["author"] == user["m.author"], ["lat"]].values[0])
        # data.loc[data["author"] == user["n.author"], ["retweeted"]] = user["m.author"]
        try:
            print(data.loc[data["author"] == user["m.author"], ["lat"]].values[0][0])
            data.loc[data["author"] == user["n.author"], ["lat2"]] = data.loc[data["author"] == user["m.author"], ["lat"]].values[0][0]
            data.loc[data["author"] == user["n.author"], ["lon2"]] = data.loc[data["author"] == user["m.author"], ["lon"]].values[0][0]
        except Exception as e:
            continue

    # making separate last name column from new data frame 
    # data["Last Name"]= new[1] 
  
    #Make the background map
    m = Basemap(projection='merc',llcrnrlat=-80,urcrnrlat=80,llcrnrlon=-180,urcrnrlon=180,resolution='c')
    # m = Basemap(llcrnrlon=-119,llcrnrlat=22,urcrnrlon=-64,urcrnrlat=49,
    #     projection='lcc',lat_1=33,lat_2=45,lon_0=-95,resolution='c')    
    m.drawmapboundary(fill_color='#A6CAE0', linewidth=0)
    m.fillcontinents(color='grey', alpha=0.3)
    m.drawcoastlines(linewidth=0.1, color="white")
    
#     # prepare a color for each point depending on the continent.
#     # data['labels_enc'] = pd.factorize(data['country'])[0]


    data = data[np.isfinite(data['lon2'])]
    data = data[np.isfinite(data['lat2'])]


#     print(data)
    pickle.dump( data, open( map_name+".p", "wb" ) )

    # Add a point per position
    #doing one day
    print("plotting days")
    # print(type(data['lon'].tolist()))
    #https://stackoverflow.com/questions/45512429/python-basemap-drawgreatcircle-with-arrow-end-cap
    for index, row in data.iterrows():
        # print(row["lon"])
        line, = m.drawgreatcircle(row['lon'], row['lat'],row['lon2'], row['lat2'],linewidth=3,alpha=0.6,color='r')

        path = line.get_path()  # get path from the great circle
        startx,starty = m(row['lon'],row['lat'])
        m.plot(startx,starty, linestyle='none',marker='o', color='r', markersize=15)

        head = m(row['lon2'],row['lat2'])             # get location of arrow's head (at London)
        # m.plot(head[0], head[1], marker='o', color='r', markersize=30)

        tail = path.vertices[-len(path)//6]  # get location of arrow's tail
        # draw annotation with arrow in 'red' color
        # blank text is specified, because we need the arrow only
        # adjust facecolor and other arrow properties as needed
        plt.annotate('',
            xy=(head[0], head[1]), 
            xycoords='data',
            xytext=(tail[0], tail[1]), 
            textcoords='data',
            size=22,
            arrowprops=dict(headwidth=10, \
                            headlength=20, \
                            facecolor="red", \
                            alpha = 0.6,\
                            edgecolor="none", \
                            connectionstyle="arc3, rad=0.001") )
        


    # m.scatter(data['lon'], data['lat'], s=data["location"].value_counts()/3, alpha=1,cmap="terrain")
    # create animation
    # ani = matplotlib.animation.FuncAnimation(fig, animate,frames=200,interval=100)
    # ani.save(str(map_name)+".gif",fps=10)
    plt.text( -170, -58,'College Admissions Scandal', ha='left', va='bottom', size=9, color='#555555' )
    # Save as png
    plt.savefig(str(map_name)+'.png',bbox_inches='tight')

    return


def get_interact_loc(relations_dict, dataframe_,map_name):
    print("Creating map")
    data = dataframe_
    # data["retweeted"] = 0
    data["lat2"] = np.nan
    data["lon2"] = np.nan
    for user in tqdm(relations_dict):
        # print(data.loc[data["author"] == user["m.author"], ["lat"]].values[0])
        # data.loc[data["author"] == user["n.author"], ["retweeted"]] = user["m.author"]
        try:
            print(data.loc[data["author"] == user["m.author"], ["lat"]].values[0][0])
            data.loc[data["author"] == user["n.author"], ["lat2"]] = data.loc[data["author"] == user["m.author"], ["lat"]].values[0][0]
            data.loc[data["author"] == user["n.author"], ["lon2"]] = data.loc[data["author"] == user["m.author"], ["lon"]].values[0][0]
        except Exception as e:
            continue
    
    data = data[np.isfinite(data['lon2'])]
    data = data[np.isfinite(data['lat2'])]

    pickle.dump( data, open( map_name+".p", "wb" ) )
    return


#script stuff here
#get locations
# in_US_city_, in_US_no_city_, not_US_city_, not_US_no_city_ = get_US_location()       
# get_location_not_US(not_US_city_,not_US_no_city_) 
# merge_capital_to_US_data()

#get relations dict from user relationships
# all_data = pickle.load( open( "data.p", "rb" ) )
# # mentions_dict = get_mention_data()
# # get_interact_loc(mentions_dict,all_data,"all_months_mentions2")
# retweet_dict = get_retweet_data()
# replies_dict = get_replies_data()
# get_interact_loc(retweet_dict,all_data,"all_months_retweet2")
# get_interact_loc(replies_dict,all_data,"all_months_replies2")

dates_data = pickle.load( open( "dates_added_data2.p", "rb" ) )    
mentions_data = pickle.load( open( "dates_added_data_replies2.p", "rb" ) )
# mentions_data = pickle.load( open( "all_months_mentions2.p", "rb" ) )
# reply_data = pickle.load( open( "all_months_replies2.p", "rb" ) )
get_every_day(dates_data,mentions_data)
# get_every_day()

    
            



