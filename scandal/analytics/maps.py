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
    for user in users.values():
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
    with open("uscitiesv1.5.csv", "r") as inputMapData:        
        # writer = csv.writer(outputUSMapData)
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
                # writer.writerow(user_location)
        # print(US_capital)
        for user_location in in_US_no_city:
            if str(user_location[1]) in US_capital:
                lat_lng = (US_capital[str(user_location[1])]).split(",")
                user_location.append(lat_lng[0])
                user_location.append(lat_lng[1])
                # writer.writerow(user_location)
                # print(user_location)

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


    for user in user_time_list:
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
    three_day_data =  data.loc[data['three_day'] == 1]
    week_day_data =  data.loc[data['one_week'] == 1]
    month_day_data =  data.loc[data['one_month'] == 1]
    month2_day_data =  data.loc[data['two_month'] == 1]

    return one_day_data,three_day_data,week_day_data,month_day_data,month2_day_data


def create_map(dataframe_,map_name):
    print("Creating map")
    # with open("test_map_data.csv","r") as inputMap:
        # reader = csv.reader(inputMap)
        # for row in reader:
            
        # Set the dimension of the figure
    my_dpi=96
    plt.figure(figsize=(2600/my_dpi, 1800/my_dpi), dpi=my_dpi)
    
    data = dataframe_
  
    # making separate last name column from new data frame 
    # data["Last Name"]= new[1] 
  
    # Make the background map
    m=Basemap(llcrnrlon=-180, llcrnrlat=-65,urcrnrlon=180,urcrnrlat=80)
    m.drawmapboundary(fill_color='#A6CAE0', linewidth=0)
    m.fillcontinents(color='grey', alpha=0.3)
    m.drawcoastlines(linewidth=0.1, color="white")
    
    # prepare a color for each point depending on the continent.
    data['labels_enc'] = pd.factorize(data['country'])[0]
    

    # print(data)
    # Add a point per position
    #doing one day
    print("plotting days")
    m.scatter(data['lon'], data['lat'], s=data["location"].value_counts()/3, alpha=1,cmap="terrain")
    # copyright and source data info
    plt.text( -170, -58,'College Admissions Scandal', ha='left', va='bottom', size=9, color='#555555' )
    # Save as png
    plt.savefig(str(map_name)+'.png', bbox_inches='tight')

    

    
    


    
#need to figure out most effect way to get latitude and longitude without data
            
# in_US_city_, in_US_no_city_, not_US_city_, not_US_no_city_ = get_US_location()       
# get_location_not_US(not_US_city_,not_US_no_city_) 
# merge_capital_to_US_data()
# create_map()
users_time_ = get_different_times()
one_day_data_,three_day_data_,week_day_data_,month_day_data_,month2_day_data_ = create_data_frame_for_map(users_time_)
create_map(one_day_data_,"1day")
create_map(three_day_data_,"3day")
create_map(week_day_data_,"1week")
create_map(month_day_data_,"1month")
create_map(month2_day_data_,"2month")