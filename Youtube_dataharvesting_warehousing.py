#-------------------------------------------------------------------------#
#  Import all the required components                                     #
#-------------------------------------------------------------------------#

import streamlit as st
import googleapiclient.discovery
import pandas as pd
import pprint
import mysql.connector


#-------------------------------------------------------------------------#
#  Connect to MySQL                                                       #
#-------------------------------------------------------------------------#

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="qwerty"
)
cursor = conn.cursor()
cursor.execute("use youtube")

#-------------------------------------------------------------------------#
#  Connect to YouTube API v3                                              #
#-------------------------------------------------------------------------#
#  Use your Api key Id in the place of use_your_api_id                    #
#-------------------------------------------------------------------------#

def api_connection():
        Api_Id="use_your_api_id"
        api_service="youtube"
        api_version="v3"
        youtube=googleapiclient.discovery.build(api_service,api_version,developerKey=Api_Id)
        return youtube

youtube=api_connection()
print(youtube)


#-------------------------------------------------------------------------#
#  This Below function will fetch the details of Channel Details          #
#-------------------------------------------------------------------------#
#  Channel Id should be passed as input                                   #
#-------------------------------------------------------------------------#

def get_channel_info(channel_id):
    request=youtube.channels().list(
                    part="snippet,ContentDetails,statistics",
                    id=channel_id
    )
    response=request.execute()

    channel_lists=[]
    for i in response['items']:
        lists=[]
        lists.append(i["id"])
        lists.append(i["snippet"]["title"])
        lists.append(int(i["statistics"]["viewCount"]))
        lists.append(i["snippet"]["description"])
        channel_tuples=tuple(lists)
        channel_lists.append(channel_tuples)
        # print(channel_lists)

    return channel_lists


#-------------------------------------------------------------------------#
#  This Below function will fetch the details of Playlists belong to      #
#  particular channel                                                     #
#-------------------------------------------------------------------------#
#  Channel Id should be passed as input                                   #
#-------------------------------------------------------------------------#

def get_playlist_details(channel_id):
        next_page_token=None
        all_playlist_ids=[]

        while True:
                request=youtube.playlists().list(
                        part='snippet,contentDetails',
                        channelId=channel_id,
                        maxResults=50,
                        pageToken=next_page_token
                )
                response=request.execute()
                # pprint.pprint(response)
                # break
                
                for item in response['items']:
                        playlists=[]
                        playlists.append(item['id'])
                        playlists.append(item['snippet']['channelId'])
                        playlists.append(item['snippet']['title'])
                        tuples=tuple(playlists)
                        all_playlist_ids.append(tuples)
                        
                next_page_token=response.get('nextPageToken')
                if next_page_token is None:
                        break
                
        return all_playlist_ids

#-------------------------------------------------------------------------#
#  This Below function will fetch the details of video ids belong to      #
#  particular channel                                                     #
#-------------------------------------------------------------------------#
#  Channel Id should be passed as input                                   #
#-------------------------------------------------------------------------# 

def get_videos_ids(channel_id):
    video_ids=[]
    next_page_token=None
    total_videos=0

    response=youtube.channels().list(id=channel_id,
                                    part='contentDetails').execute()
    Playlist_Id=response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    while True:
        response1=youtube.playlistItems().list(
                                            part='snippet',
                                            playlistId=Playlist_Id,
                                            maxResults=50,
                                            pageToken=next_page_token).execute()
        for i in range(len(response1['items'])):
            video_ids.append(response1['items'][i]['snippet']['resourceId']['videoId'])
            total_videos=total_videos+1
        next_page_token=response1.get('nextPageToken')

        if next_page_token is None:
            break

    print(total_videos)
    return video_ids

#-------------------------------------------------------------------------#
#  This Below function will fetch the details of video info belong to     #
#  particular channel                                                     #
#-------------------------------------------------------------------------#
#  Video Ids should be passed as input                                    #
#-------------------------------------------------------------------------# 
 
def get_video_info(video_ids, channel_name):
    
    all_video_details=[]
    for video_id in video_ids:
        request=youtube.videos().list(
            part="snippet,ContentDetails,statistics",
            id=video_id
        )
        response=request.execute()
        # pprint.pprint(response)
        # break
        
        each_video_details=[]
        
        for item in response["items"]:

            each_video_details.append(item['id'])
            each_video_details.append(item['snippet']['title'])
            each_video_details.append(item['snippet'].get('description'))
            each_video_details.append(channel_name)
           
            published_date=item['snippet']['publishedAt'][0:10]+" "+item['snippet']['publishedAt'][11:19]
            each_video_details.append(published_date)

            if (item['statistics'].get('viewCount'))==None:
                each_video_details.append(0)
            else:
                each_video_details.append(int(item['statistics'].get('viewCount')))

            if (item['statistics'].get('likeCount'))==None:
                each_video_details.append(0)
            else:
                each_video_details.append(int(item['statistics'].get('likeCount')))

            if (item['statistics']['favoriteCount'])==None:
                each_video_details.append(0)
            else:
                each_video_details.append(int(item['statistics']['favoriteCount']))

            if (item['statistics'].get('commentCount'))==None:
                each_video_details.append(0)
            else:
                each_video_details.append(int(item['statistics'].get('commentCount')))

            #-------------------------------------------------------------------------#
            # This process is for converting Duration to integer format               #
            #-------------------------------------------------------------------------# 

            duration=""
            duration=item['contentDetails']['duration']
            # print(duration)

            if len(duration)==4:
                if duration[3]=='H' and len(duration)==4:
                    total_seconds=3600*int(duration[2])
                    # print(total_seconds)

                if duration[3]=='M' and len(duration)==4:
                    total_seconds=60*int(duration[2])
                    # print(total_seconds)

                if duration[3]=='S' and len(duration)==4:
                    total_seconds=int(duration[2])
                    # print(total_seconds)
            #################################################################################
            if len(duration)==5:
                if duration[4]=='H' and len(duration)==5:
                    total_seconds=3600*int(duration[2:4])
                    # print(total_seconds)

                if duration[4]=='M' and len(duration)==5:
                    total_seconds=60*int(duration[2:4])
                    # print(total_seconds)

                if duration[4]=='S' and len(duration)==5:
                    total_seconds=int(duration[2:4])
                    # print(total_seconds)
            #############################################################################
            #lenght of duration is 6
            if len(duration)==6:
                if duration[3]=='H' and duration[5]=='S':
                    total_seconds=(3600*int(duration[2]))+int(duration[4])
                    # print(total_seconds)

                if duration[3]=='H' and duration[5]=='M':
                    total_seconds=(3600*int(duration[2]))+(60*int(duration[4]))
                    # print(total_seconds)

                if duration[3]=='M' and duration[5]=='S':
                    total_seconds=(60*int(duration[2]))+int(duration[4])
                    # print(total_seconds)

            #############################################################################
            #lenghthof duration 7
            if len(duration)==7:
                if duration[3]=='H' and duration[6]=='S':
                    total_seconds=(3600*int(duration[2]))+int(duration[4:6])
                    # print(total_seconds)

                if duration[3]=='H' and duration[6]=='M':
                    total_seconds=(3600*int(duration[2]))+(60*int(duration[4:6]))
                    # print(total_seconds)

                if duration[3]=='M' and duration[6]=='S':
                    total_seconds=(60*int(duration[2]))+int(duration[4:6])
                    # print(total_seconds)

                if duration[4]=='H' and duration[6]=='S':
                    total_seconds=(3600*int(duration[2:4]))+int(duration[5])
                    # print(total_seconds)

                if duration[4]=='H' and duration[6]=='M':
                    total_seconds=(3600*int(duration[2:4]))+(60*int(duration[5]))
                    # print(total_seconds)

                if duration[4]=='M' and duration[6]=='S':
                    total_seconds=(60*int(duration[2:4]))+int(duration[5])
                    # print(total_seconds)

            #############################################################################
            # lenght of duration 8
            if len(duration)==8:
                if duration[4]=='H' and duration[7]=='M':
                    total_seconds=(3600*int(duration[2:4]))+(60*int(duration[5:7]))
                    # print(total_seconds)

                if duration[4]=='H' and duration[7]=='S':
                    total_seconds=(3600*int(duration[2:4]))+int(duration[5:7])
                    # print(total_seconds)

                if duration[4]=='M' and duration[7]=='S':
                    total_seconds=(60*int(duration[2:4]))+int(duration[5:7])
                    # print(total_seconds)

                if duration[3]=='H' and duration[5]=='M'and duration[7]=='S':
                    total_seconds=(3600*int(duration[2]))+(60*int(duration[4]))+int(duration[6])
                    # print(total_seconds)

            #############################################################################
            # lenght of duration 9
            if len(duration)==9:
                if duration[4]=='H' and duration[6]=='M'and duration[8]=='S':
                    total_seconds=(3600*int(duration[2:4]))+(60*int(duration[5]))+int(duration[7])
                    # print(total_seconds)

                if duration[3]=='H' and duration[6]=='M'and duration[8]=='S':
                    total_seconds=(3600*int(duration[2]))+(60*int(duration[4:6]))+int(duration[7])
                    # print(total_seconds)

                if duration[3]=='H' and duration[5]=='M'and duration[8]=='S':
                    total_seconds=(3600*int(duration[2]))+(60*int(duration[4]))+int(duration[6:8])
                    # print(total_seconds)

            #############################################################################
            # lenght of duration 10

            if len(duration)==10:
                if duration[4]=='H' and duration[7]=='M'and duration[9]=='S':
                    total_seconds=(3600*int(duration[2:4]))+(60*int(duration[5:7]))+int(duration[8])
                    # print(total_seconds)

                if duration[4]=='H' and duration[6]=='M'and duration[9]=='S':
                    total_seconds=(3600*int(duration[2:4]))+(60*int(duration[5]))+int(duration[7:9])
                    # print(total_seconds)

                if duration[3]=='H' and duration[6]=='M'and duration[9]=='S':
                    total_seconds=(3600*int(duration[2]))+(60*int(duration[4:6]))+int(duration[7:9])
                    # print(total_seconds)

            #############################################################################
            # lenght of duration 11
            if len(duration)==11:
                if duration[4]=='H' and duration[7]=='M'and duration[10]=='S':
                    total_seconds=(3600*int(duration[2:4]))+(60*int(duration[5:7]))+int(duration[8:10])
                    # print(total_seconds)

            #-------------------------------------------------------------------------#
            # Duration converting process ends here                                   #
            #-------------------------------------------------------------------------#

            each_video_details.append(total_seconds)
            each_video_details.append(item['snippet']['thumbnails']['default']['url'])
            each_video_details.append(item['contentDetails']['caption'])
            video_info_tuples=tuple(each_video_details)
            # print(video_info_tuples)
            
            # print(all_video_details)
            
        all_video_details.append(video_info_tuples)
        #print(all_video_details)
    
    return all_video_details

#-------------------------------------------------------------------------#
# This below function will fetch the comment details of each videos       #
#-------------------------------------------------------------------------#
# Video Ids should be passed as input                                     #
#-------------------------------------------------------------------------#

def get_comment_info(video_ids):
    comment_details_lists=[]
    try:
        for video_id in video_ids:
            request=youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=50
            )
            response=request.execute()

            for item in response['items']:
                each_comment_details=[]
                each_comment_details.append(item['snippet']['topLevelComment']['id'])
                each_comment_details.append(item['snippet']['topLevelComment']['snippet']['videoId'])
                each_comment_details.append(item['snippet']['topLevelComment']['snippet']['textDisplay'])
                each_comment_details.append(item['snippet']['topLevelComment']['snippet']['authorDisplayName'])
                date_time=item['snippet']['topLevelComment']['snippet']['publishedAt'][0:10]+" "+item['snippet']['topLevelComment']['snippet']['publishedAt'][11:19]
                each_comment_details.append(date_time)
                each_comment_details_tuple=tuple(each_comment_details)
                comment_details_lists.append(each_comment_details_tuple)
    except:
        pass
    return comment_details_lists

#-------------------------------------------------------------------------#
# This below function will insert the fetched channel details to channel  #
# table                                                                   #
#-------------------------------------------------------------------------#

def insert_channel_record(channel_details):

    i=0
    insert_no_error=True

    while i<len(channel_details):
        # print(channel_details)            
        insert_query_channel=f"INSERT INTO youtube.channel (channel_id, channel_name, channel_views, channel_description) VALUES {channel_details[i]}"
        try:
            cursor.execute(insert_query_channel)
            # print("Insert Successful in Channel Table")
        except mysql.connector.Error as err:
            # print(f"Error: {err}")
            st.write(f"Error : {err}")
            insert_no_error=False
            break
        i=i+1

    if insert_no_error==True:
        st.write("Channel details fecthed and stored successfully")
    conn.commit()

#-------------------------------------------------------------------------#
# This below function will insert the fetched playlists details to        #
# playlist table                                                          #
#-------------------------------------------------------------------------#

def insert_playlist_record(playlist_details):
        
        i=0
        insert_no_error=True

        while i<len(playlist_details):
            playlist_details_row=playlist_details[i]
            insert_query_playlist=f"insert into youtube.playlist values {playlist_details_row}"
            # print(insert_query_playlist)
            try:
                cursor.execute(insert_query_playlist)
            except mysql.connector.Error as err:
                # print(f"Error: {err}")
                st.write(f"Error : {err}")
                insert_no_error=False
                break
            i=i+1

        if insert_no_error==True:
            st.write("Playlist details of channel fecthed and stored successfully")

        conn.commit()

#-------------------------------------------------------------------------#
# This below function will insert the fetched video details to video table#
#-------------------------------------------------------------------------#
def insert_video_record(video_details):
        
        i=0
        insert_no_error=True

        while i<len(video_details):
            insert_query_video=f"insert into youtube.video (video_id, video_name, video_description, channel_name, published_date, view_count, like_count, favorite_count, comment_count, duration, thumbnail, caption_status) VALUES {video_details[i]}"
    #       print(insert_query_video)
            try:
                cursor.execute(insert_query_video)
            except mysql.connector.Error as err:
                # print(f"Error: {err}")
                st.write(f"Error : {err}")
                insert_no_error=False
                break
            i=i+1

        if insert_no_error==True:
            st.write("Video details of channel fecthed and stored successfully")
        conn.commit()

#-------------------------------------------------------------------------#
# This below function will insert the fetched comment details to comment  #
# table                                                                   #
#-------------------------------------------------------------------------#
def insert_comment_record(comment_details):
        
        i=0
        insert_no_error=True

        while i<len(comment_details):
            insert_query_comment=f"insert into youtube.comment VALUES {comment_details[i]}"
            # print(insert_query_comment)
            try:
                cursor.execute(insert_query_comment)
            except mysql.connector.Error as err:
                # print(f"Error: {err}")
                st.write(f"Error : {err}")
                insert_no_error=False
                break
            i=i+1

        if insert_no_error==True:
            st.write("Comment details of each video fecthed and stored successfully")
        
        conn.commit()

#-------------------------------------------------------------------------#
# This below function will create selected table if it not exists         #
#-------------------------------------------------------------------------#
def create_table_fun(select_table):

    if select_table=="CHANNEL":
        try:
            create_query='''create table if not exists youtube.channel(channel_id varchar(255) not null,
                                                            channel_name varchar(255),
                                                            channel_type varchar(255),
                                                            channel_views int,
                                                            channel_description text,
                                                            channel_status varchar(255),
                                                            primary key(channel_id))'''
            cursor.execute(create_query)
            # print("Table Created")
            conn.commit()
            st.write("CHANNEL Table created sucessfully")
        except mysql.connector.Error as err:
            # print(f"Error: {err}")
            st.write(f"Error : {err}")

    if select_table=="PLAYLIST":
        try:
            create_query='''create table if not exists youtube.playlist(playlist_id varchar(255),
                                                            channel_id varchar(255),
                                                            playlist_name varchar(255),
                                                            primary key(playlist_id),
                                                            foreign key (channel_id) REFERENCES channel(channel_id))'''
            cursor.execute(create_query)
            conn.commit()
            st.write("PLAYLIST Table created sucessfully")
        except mysql.connector.Error as err:
            # print(f"Error: {err}")
            st.write("Make sure CHANNEL table created")
            st.write(f"Error : {err}")
    
    if select_table=="VIDEO":
        try:
            create_query='''create table if not exists youtube.video(video_id varchar(255),
                                                            playlist_id varchar(255),
                                                            video_name varchar(255),
                                                            video_description text,
                                                            channel_name varchar(255),
                                                            published_date datetime,
                                                            view_count int,
                                                            like_count int,
                                                            dislike_count int,
                                                            favorite_count int,
                                                            comment_count int,
                                                            duration int,
                                                            thumbnail varchar(255),
                                                            caption_status varchar(255),
                                                            primary key(video_id),
                                                            foreign key (playlist_id) REFERENCES playlist(playlist_id))'''
            cursor.execute(create_query)
            conn.commit()
            st.write("VIDEO Table created sucessfully")
        except mysql.connector.Error as err:
            # print(f"Error: {err}")
            st.write("Make sure PLAYLIST table created")
            st.write(f"Error : {err}")
    
    if select_table=="COMMENT":
        try:
            create_query='''create table if not exists youtube.comment(comment_id varchar(255),
                                                            video_id varchar(255),
                                                            comment_text text,
                                                            comment_author varchar(255),
                                                            comment_published_date datetime,
                                                            primary key(comment_id),
                                                            foreign key (video_id) REFERENCES video(video_id))'''
            cursor.execute(create_query)
            conn.commit()
            st.write("COMMENT Table created sucessfully")
        except mysql.connector.Error as err:
            # print(f"Error: {err}")
            st.write("Make sure VIDEO table created")
            st.write(f"Error : {err}")

#-------------------------------------------------------------------------#
# This below function will drop seleceted table                           #
#-------------------------------------------------------------------------#
def drop_table_fun(select_table):
    if select_table=="CHANNEL":
        try:
            drop_query='''drop table youtube.channel'''
            cursor.execute(drop_query)
            conn.commit()
            st.write("CHANNEL Table dropped sucessfully")
        except mysql.connector.Error as err:
            # print(f"Error: {err}")
            st.write("Make sure PLAYLIST table dropped")
            st.write(f"Error : {err}")
    
    if select_table=="PLAYLIST":
        try:
            drop_query='''drop table youtube.playlist'''
            cursor.execute(drop_query)
            conn.commit()
            st.write("PLAYLIST Table dropped sucessfully")
        except mysql.connector.Error as err:
            # print(f"Error: {err}")
            st.write("Make sure VIDEO table dropped")
            st.write(f"Error : {err}")
    
    if select_table=="VIDEO":
        try:
            drop_query='''drop table youtube.video'''
            cursor.execute(drop_query)
            conn.commit()
            st.write("VIDEO Table dropped sucessfully")
        except mysql.connector.Error as err:
            # print(f"Error: {err}")
            st.write("Make sure COMMENT table dropped")
            st.write(f"Error : {err}")
    
    if select_table=="COMMENT":
        try:
            drop_query='''drop table youtube.comment'''
            cursor.execute(drop_query)
            conn.commit()
            st.write("COMMENT Table dropped sucessfully")
        except mysql.connector.Error as err:
            # print(f"Error: {err}")
            st.write(f"Error : {err}")

#-------------------------------------------------------------------------#
# This below function will delete all the records from seleceted table    #
#-------------------------------------------------------------------------#
def delete_record_fun(select_table):
    if select_table=="CHANNEL":
        try:
            delete_query='''delete from youtube.channel'''
            cursor.execute(delete_query)
            conn.commit()
            st.write("All records in CHANNEL table deleted sucessfully")
        except mysql.connector.Error as err:
            # print(f"Error: {err}")
            st.write("Make sure related PLAYLIST table records are deleted")
            st.write(f"Error : {err}")
    
    if select_table=="PLAYLIST":
        try:
            delete_query='''delete from youtube.playlist'''
            cursor.execute(delete_query)
            conn.commit()
            st.write("All records in PLAYLIST table deleted sucessfully")
        except mysql.connector.Error as err:
            # print(f"Error: {err}")
            st.write("Make sure related VIDEO table records are deleted")
            st.write(f"Error : {err}")
    
    if select_table=="VIDEO":
        try:
            delete_query='''delete from youtube.video'''
            cursor.execute(delete_query)
            conn.commit()
            st.write("All records in VIDEO table deleted sucessfully")
        except mysql.connector.Error as err:
            # print(f"Error: {err}")
            st.write("Make sure related COMMENT table records are deleted")
            st.write(f"Error : {err}")
    
    if select_table=="COMMENT":
        try:
            delete_query='''delete from youtube.comment'''
            cursor.execute(delete_query)
            conn.commit()
            st.write("All records in COMMENT table deleted sucessfully")
        except mysql.connector.Error as err:
            # print(f"Error: {err}")
            st.write(f"Error : {err}")

#-------------------------------------------------------------------------#
# Streamlit web page starts here                                          #
#-------------------------------------------------------------------------#  
st.set_page_config(layout="wide")

from streamlit_option_menu import option_menu
#-------------------------------------------------------------------------#
# Side Option Menu with three categories                                  #
#-------------------------------------------------------------------------# 

with st.sidebar:
    st.title(":red[Contents]")
   
    selected=option_menu( menu_title= "Overview",
          options=["Home","Collecting the data","Queries"],
          icons=["house-door","collection-play-fill","question-circle-fill"],
          menu_icon="book-fill",
          default_index=0)

#-------------------------------------------------------------------------#
# If Home button is selected will display the insights of project         #
#-------------------------------------------------------------------------# 

if selected=="Home":
    st.divider()
    st.text('''            
Data harvesting is the process of gathering data from numerous sources, such as 
websites, applications, and social media platforms, and storing it in a database in 
order to make assumptions.

Here we have created a Streamlit application that allows users to access and analyze data 
from multiple YouTube channels. The application should have the following features:
     
    1. Ability to input a YouTube channel ID and retrieve all the relevant data 
        (Channel name, subscribers, total video count, playlist ID, video ID, likes, 
        dislikes, comments of each video) using Google API.
            
    2. Store the data in MySQL Database.
            
    3. Ability to collect data for of different YouTube channels and store them 
        in the data lake by clicking a button.
                      
    4. Ability to search and retrieve data from the SQL database using different
        search options to get channel details.''')
        
    st.divider()
#-------------------------------------------------------------------------#
# Collecting the data Page will do the following process                  #
#   1. Table Creation, Deletion and Delete Records                        #
#   2. Fetch records of Youtube channel and store it in MySQL DB          # 
#-------------------------------------------------------------------------#

if selected=="Collecting the data":
    st.divider()
    st.title("YouTube Data Harvesting and Warehousing using SQL and Streamlit")
    st.divider()

#-------------------------------------------------------------------------#
# Table operation and Maintenance part                                    #
#-------------------------------------------------------------------------#

    select_table=st.radio("Select table :",("CHANNEL","PLAYLIST","VIDEO","COMMENT"), horizontal=True)

    create_table, drop_table, delete_records = st.columns(3)

    if create_table.button(label='Create Table', type="primary", help="This will create selected table"):           
        create_table_fun(select_table)

    if drop_table.button(label='Drop Table', type="primary", help="This will drop selected table"):
        drop_table_fun(select_table)

    if delete_records.button(label='Delete Records', type="primary", help="This will delete all the records from sleceted table"):
        delete_record_fun(select_table)

    st.divider()

#-------------------------------------------------------------------------#
# Youtube Data harvesting and warehousing                                 #
#-------------------------------------------------------------------------#

    youtube_channel_id=st.text_input("Enter YouTube Channel ID:", placeholder="Enter valid youtube channel id")
    extract_details=st.button(label="Extract Details",type="primary",
                         help="Input valid YouTube channel id and click Extract Details")


    if extract_details:
        if youtube_channel_id[0]==" " or youtube_channel_id[-1]==" ":
            st.write("Enter valid youtube channel ID")
        else:

#-------------------------------------------------------------------------#
# Call function to get details of channel                                 #
#-------------------------------------------------------------------------#
            channel_details=get_channel_info(youtube_channel_id)
            channel_name=channel_details[0][1]
            insert_channel_record(channel_details)    

#-------------------------------------------------------------------------#
# Call function to get details of playlists                               #
#-------------------------------------------------------------------------#
            playlist_details=get_playlist_details(youtube_channel_id)
            insert_playlist_record(playlist_details)

#-------------------------------------------------------------------------#
# Call function to get video ids of youtube channel                       #
#-------------------------------------------------------------------------#
            video_ids=get_videos_ids(youtube_channel_id)
            # pprint.pprint(video_ids)

#-------------------------------------------------------------------------#
# Call function to get video info of youtube channel                      # 
#-------------------------------------------------------------------------#
            video_details=get_video_info(video_ids, channel_name)
            insert_video_record(video_details)
            # pprint.pprint(comment_details)

#-------------------------------------------------------------------------#
# Call function to get comment info of videos in youtube channel          #
#-------------------------------------------------------------------------#
            comment_details=get_comment_info(video_ids)
            insert_comment_record(comment_details)
            # pprint.pprint(comment_details)

            st.write("Youtube channel details fetched and stored in MySQL Data Base")

    st.divider()

#-------------------------------------------------------------------------#
# The below process will fetch the entire selected table and show the     #
# table in streamlit webpage                                              #
#-------------------------------------------------------------------------#

if selected=="Queries":

    st.divider()

    view_table=st.selectbox("View table :",options=["CHANNEL","PLAYLIST","VIDEO","COMMENT"])

    show_table=st.button(label="Show Table",type="primary",
                          help="This will fetch all records from table")

    if view_table=="CHANNEL" and show_table==True:
        select_query= "SELECT * FROM channel"
        cursor.execute(select_query)
        table= cursor.fetchall()
        df_all_channels= pd.DataFrame(table)
        df_all_channels.columns = ['Channel ID', 'Channel Name','Channel Type', 
                               'Channel Views', 'Channel Description', 'Channel Status']
        st.write(df_all_channels)

    elif view_table=="PLAYLIST" and show_table==True:
        select_query= "SELECT * FROM youtube.playlist order by channel_id"
        cursor.execute(select_query)
        table= cursor.fetchall()
        df_all_playlists= pd.DataFrame(table)
        df_all_playlists.columns = ['Playlist ID','Channel ID','Playlist Name']
        st.write(df_all_playlists)

    elif view_table=="VIDEO" and show_table==True:
        select_query= "SELECT * FROM youtube.video order by channel_name"
        cursor.execute(select_query)
        table= cursor.fetchall()
        df_all_videos= pd.DataFrame(table)
        df_all_videos.columns = ['Video ID', 'Playlist ID', 'Video Name',
                                'Video Description', 'Channel Name','Published Date', 'View Count',
                                'Like Count', 'Dislike Count', 'Favorite Count',
                               'Comment Count', 'Duration', 'Thumbnail', 'Caption Status']
        st.write(df_all_videos)

    elif view_table=="COMMENT" and show_table==True:
        select_query= "SELECT * FROM comment order by video_id"
        cursor.execute(select_query)
        table= cursor.fetchall()
        df_all_comments= pd.DataFrame(table)
        df_all_comments.columns = ['Comment ID', 'Video ID', 'Comment Text',
                                 'Comment Author', 'Comment Published Date']
        st.write(df_all_comments)

    st.divider()
#-------------------------------------------------------------------------#
# You have the option to select the questionaries from below option       #
#-------------------------------------------------------------------------#
    st.write("Select the details you want to see:")

    select_details=st.selectbox("View table :",
                            options=
                            ["01. What are the names of all the videos and their corresponding channels?",
                             "02. Which channels have the most number of videos, and how many videos do they have?",
                             "03. What are the top 10 most viewed videos and their respective channels?",
                             "04. How many comments were made on each video, and what are their corresponding video names?",
                             "05. Which videos have the highest number of likes, and what are their corresponding channel names?",
                             "06. What is the total number of likes and dislikes for each video, and what are their corresponding video names?",
                             "07. What is the total number of views for each channel, and what are their corresponding channel names?",
                             "08. What are the names of all the channels that have published videos in the year 2022?",
                             "09. What is the average duration of all videos in each channel, and what are their corresponding channel names?",
                             "10. Which videos have the highest number of comments, and what are their corresponding channel names?"])

    select_question=st.button(label="Submit",type="primary",
                         help="select the details you want to see")

    if select_question==True:
        if select_details[0:2]=='01':    
            question_query= "select video_name, channel_name from video"
            cursor.execute(question_query)
            table= cursor.fetchall()
            df_all_channels= pd.DataFrame(table)
            df_all_channels.columns = ['Video Name', 'Channel Name']
            st.write(df_all_channels)

        if select_details[0:2]=='02':
            question_query= "SELECT distinct(channel_name), count(video_id) as Video_count from youtube.video group by channel_name order by Video_count desc"
            cursor.execute(question_query)
            table= cursor.fetchall()
            df_all_channels= pd.DataFrame(table)
            df_all_channels.columns = ['Channel Name','Video Count']
            st.write(df_all_channels)

        if select_details[0:2]=='03':
            question_query= "SELECT video_name, channel_name from youtube.video order by view_count desc Limit 10"
            cursor.execute(question_query)
            table= cursor.fetchall()
            df_all_channels= pd.DataFrame(table)
            df_all_channels.columns = ['Video Name','Channel Name']
            st.write(df_all_channels)

        if select_details[0:2]=='04':
            question_query= "select video_name, comment_count from youtube.video"
            cursor.execute(question_query)
            table= cursor.fetchall()
            df_all_channels= pd.DataFrame(table)
            df_all_channels.columns = ['Video Name','Comment Count']
            st.write(df_all_channels)

        if select_details[0:2]=='05':
            question_query= "select channel_name, video_name, like_count from youtube.video order by like_count desc"
            cursor.execute(question_query)
            table= cursor.fetchall()
            df_all_channels= pd.DataFrame(table)
            df_all_channels.columns = ['Channel Name','Video Name','Like Count']
            st.write(df_all_channels)

        if select_details[0:2]=='06':
            question_query= "select video_name, like_count, dislike_count from youtube.video"
            cursor.execute(question_query)
            table= cursor.fetchall()
            df_all_channels= pd.DataFrame(table)
            df_all_channels.columns = ['Video Name','Like Count','Dislike Count']
            st.write(df_all_channels)

        if select_details[0:2]=='07':
            question_query= "select video_name, like_count, dislike_count from youtube.video"
            cursor.execute(question_query)
            table= cursor.fetchall()
            df_all_channels= pd.DataFrame(table)
            df_all_channels.columns = ['Video Name','Like Count','Dislike Count']
            st.write(df_all_channels)

        if select_details[0:2]=='08':
            question_query= "select distinct(channel_name), year(published_date) from youtube.video where year(published_date)='2022'"
            cursor.execute(question_query)
            table= cursor.fetchall()
            df_all_channels= pd.DataFrame(table)
            df_all_channels.columns = ['Channel Name','Published Year']
            st.write(df_all_channels)

        if select_details[0:2]=='09':
            question_query= "select channel_name, avg(duration) from youtube.video group by channel_name"
            cursor.execute(question_query)
            table= cursor.fetchall()
            df_all_channels= pd.DataFrame(table)
            df_all_channels.columns = ['Channel Name','Average Video Duration in Sec']
            st.write(df_all_channels)

        if select_details[0:2]=='10':
            question_query= "select video_name, channel_name, comment_count from youtube.video order by comment_count desc"
            cursor.execute(question_query)
            table= cursor.fetchall()
            df_all_channels= pd.DataFrame(table)
            df_all_channels.columns = ['Video Name', 'Channel Name', 'Comment Count']
            st.write(df_all_channels)

    st.divider()
