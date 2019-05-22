import sys
import csv
from graph import *
#https://python-graph-gallery.com/300-draw-a-connection-line/
#https://python-graph-gallery.com/315-a-world-map-of-surf-tweets/

def get_location():
    users = create_user_nodes()
    total_users_location = []
    # print(users)
    #https://locationiq.com/docs#forward-geocoding
    for user in users.values():
        location_list = (user.location).split(",")
        

        if (location_list[2] != "" or location_list[1] != "") and location_list[0] != "":
            print(location_list)
            total_users_location.append(user.location)

    return len(total_users_location),len(users)

#need to figure out most effect way to get latitude and longitude without data
            
print(get_location())            

