"""
to access desktop site and play around with user spotify lists:
'https://open.spotify.com/user/[userId]',
    
"""

from __future__ import unicode_literals
import youtube_dl
#https://pypi.org/project/youtube_dl/
import json
import sys
import spotipy
#https://spotipy.readthedocs.io/en/latest/
import yaml
import os
import spotipy.util as util
from pprint import pprint
#used for debugging, if you want to print json
import datetime
import argparse

#
#displays welcome/help message
def display_help(message):
    text="""\
        ------------------------
        WELCOME TO YOUTUBE_SPFY!
        ------------------------"""

    if message==1:
        text+="""\

        Before using, youtube_spfy must be configured with a username, client_id, client_secret and redirect_uri

        For instructions, please refer to the youtube_spfy readme file, found at our github:
        https://github.com/ze-e/youtube_spfy
        """
    elif message==2:
        text+="""\

        HOW TO USE:

        1. create a new playlist from youtube URL:
        youtube_spfy.py --source [url]
        youtube_spfy.py -s [url]

        2.create a new playlist from youtube URL, with name [Name]
        youtube_spfy.py --source [url] --name [Name]
        youtube_spfy.py -s [url] -n [Name]

        3.add songs from youtube URL to existing Spotify playlist, with playlist id [Id] or name [Name]
        youtube_spfy.py --source [url] --name [Name/Id]
        youtube_spfy.py --s [url] -n [Name/Id]

        4.skip json creation by adding "True".
        youtube_spfy.py --source [url] --name [Name/Id] --skipJSON [True]
        youtube_spfy.py -s [url] -n [Name/Id] -skip [True]

        - - - - - - - - - - - - - - - - - -

        """

    print(text)
    sys.exit()

#
#loads user credentials for Spotify
def load_config():
    global user_config
    stream = open('config.yaml')
    user_config = yaml.load(stream)

#
#creates json text file if none exists
def firstRun():
    data=[]
    with open('data.txt', 'w') as outfile:  
        json.dump(data, outfile)
#
#logs our results
class Log:
    logText={}
    logText['song_not_found']=[]
    logText['song_renamed']=[]
    logText['failure']=[]   
    logText['success']=[]   
    logText['date']=str(datetime.datetime.now())

    def __init__(self):
        if os.path.exists('log.txt'):
            pass
        else:   
            with open('log.txt', 'w') as outfile:  
                json.dump(self.logText, outfile)

    def noResults(self,item):
        self.logText['song_not_found'].append({
            'item' : item,
            'result' :'song not found on spotify'
        })

    def renamed(self,old,new):
        self.logText['song_renamed'].append({
            'item' : old,
            'renamed to': new
        })
    def failure(self,item_number,item_title,item_id,result):
        self.logText['failure'].append({
            'item' : item_number,
            'title' : item_title,
            'id' : item_id,
            'result' : result
        })
    def success(self,item_number,item_title,item_id):
        self.logText['success'].append({
            'item' : item_number,
            'title' : item_title,
            'id' : item_id,
            'result' :'added'
        })

    def printLog(self):
        with open('log.txt', 'w') as outfile:  
            json.dump(self.logText, outfile)

    def results(self):
        notFoundItems=len(self.logText['song_not_found'])
        failureItems=len(self.logText['failure'])
        successItems=len(self.logText['success'])
        return notFoundItems,failureItems,successItems



#
#create json from youtube playlist, using youtube-dl (https://rg3.github.io/youtube-dl/) and the youtube_dl python module (https://pypi.org/project/youtube_dl/)
def getYoutube(url):

    print("building youtube json...")

    #create the dict and list we will add our titles into
    data = []

    ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s%(ext)s','ignoreerrors': True})

    #use youtube_dl to download the track titles, but not the files
    with ydl:
        result = ydl.extract_info(
        url,
        download=False 
        )

    #check if we returned a playlist, or a single video

    #playlist
    if 'entries' in result:
        for video in result['entries']:
            if video!=None:
                video_title = video['title']
                #cleans up the video title, removes everything after a ( or [ in a title, or after ) ] if they are the first character in the title string
                oldTitle=video_title
                video_title=cleanTitle(video_title,"(",")")
                if oldTitle!=video_title:
                    log.renamed(oldTitle,video_title)
                oldTitle=video_title
                video_title=cleanTitle(video_title,"[","]")
                if oldTitle!=video_title:
                    log.renamed(oldTitle,video_title)
                #
                data.append(video_title)

    #single video
    else:
        video = result
        video_title = video['title']
        #
        oldTitle=video_title
        video_title=cleanTitle(video_title,"(",")")
        if oldTitle!=video_title:
            log.renamed(oldTitle,video_title)
        oldTitle=video_title
        video_title=cleanTitle(video_title,"[","]")
        if oldTitle!=video_title:
            log.renamed(oldTitle,video_title)
        #
        print("title"+video_title)
        data.append(video_title)

    #write to our json file
    with open('data.txt', 'w') as outfile:  
        json.dump(data, outfile)

    with open('data.txt') as json_file:  
        data = json.load(json_file)
        for s in data:
            print(s.encode('utf-8').strip())
    return data

#
#strips characters out of the title name in order to improve search results
def cleanTitle(video_title,begin,end):
    splitCha=begin
    if splitCha in video_title:
        if video_title.find(splitCha, 0, len(video_title))!=0:
            video_title=video_title.split(splitCha, 1)[0]
            return cleanTitle(video_title,begin,end)
        elif video_title.find(splitCha, 0, len(video_title))==0:
            video_title=video_title.split(end, 1)[1]
            return cleanTitle(video_title,begin,end)
    elif splitCha not in video_title:
        return video_title

#
#return the data from the youtube jsonlist
def getList():
    with open('data.txt') as json_file:  
        data = json.load(json_file)
    return data

#
#first, we search for our youtubelist on Spotify, and create a list of those that exist on Spotify
def findSongs():
    global playlistId
    titlelist=[]

    #check if the user gave us an id or name. if they did not, create a new playlist
    if playlistId == None:
        playlistId=createPlaylist("youtube_spfy")
        existing=[]

    #if they did, check whether what they gave us was an id or a name, and search for it in the user's Spotify playlists
    elif playlistId != None:
        playlistId=findExistingPlaylist(playlistId)
        #then get the tracks on the playlist. we don't want to bother searching for those that have already been added
        tracks=[]
        existing=get_playlist_tracks(tracks,100,0,'name')

    #attempt to delete and log any tracks from the list already on the playlist. this does not work perfectly
    ytList=getList()
    if len(existing)>0:
        for s in ytList:
            if s in existing:
                print(s+" already uploaded...")
                log.failure('unknown',s,'unknown','track already uploaded')
                ytList.remove(s)
            else:
                for e in existing:
                    if s in ytList and s.find(e)!=-1:
                        print(s+" already uploaded...")
                        log.failure('unknown',s,'unknown','track already uploaded')
                        ytList.remove(s)
    #
    #get our youtube json, and search for each item by title
    print("searching for tracks...");
    for s in ytList:
        print(s.encode('utf-8').strip())
        if s!="":
            result=sp.search(s, limit=1, offset=0, type='track', market=None)
        else:
            pass
        
    #if Spotify found a result ([item]len>0) and the result is not already on our list, add it to our list
        if len(result['tracks']['items'])>0 and result not in titlelist:
            print("--found match on spotify!")
            titlelist.append(result)

    #if the result is already on our list, don't add it
        elif result in titlelist:
            print("--skipping dup track name...")

    #if it wasn't found on Spotify, log it into the "song not found" section of our log
        elif len(result['tracks']['items'])==0:
            print("--song not found on spotify...")
            title=s
            log.noResults(title)

    #
    #next we send our list of tracks to be uploaded

    return titlelist


#
#create a new playlist
def createPlaylist(playListName):
    print("creating new playlist...")
    newList={}
    newList=sp.user_playlist_create(user=user_config['username'], name=playListName, public=True)
    newListId=newList['uri']
    newListId=newListId.split(':')[2]
    print("new playlist created! "+newListId)
    return newListId
#
#search for the playlist our user gave and return its id
def findExistingPlaylist(playlistId):
    playlists = sp.user_playlists(user=user_config['username'])

    #see if the user has any playlists
    if len(playlists['items'])>0:
        for playlist in playlists['items']:

        #if the user gave us an existing playlist name (the variable can store an id or name string) return the matching playlist's id
            if playlist['name']==playlistId:
                return playlist['id']
    
        #if the user gave us an existing playlist id, just return the id they gave us
            elif playlist['id']==playlistId:
                return playlistId
    
        #if the user's name doesn't match an existing playlist, then create a new playlist using the name they gave us as the name, and return the new playlist's id
            else:
                print("could not find playlist name or id!")
                newPlaylistId=createPlaylist(playlistId)
                return newPlaylistId

    #if they have no playlists, then create a new playlist using the name they gave us as the name, and return the new playlist's id
    else:
        print("user has no playlists!")
        newPlaylistId=createPlaylist(playlistId)
        return newPlaylistId

#
#this gets all tracks from a playlist
#it is used by add_batch() to make sure we don't add any tracks we have already added

#
#Spotify only lets us return >100 results from our playlist at a time, so we have to split our playlist into batches, using the offset parameter
#tracks[] is the list of track ids on our playlist
#maxTracks is the maximum amount of tracks in a batch (100)
#totalTracks is the number we have processed. Each batch, we increase the offset by the amount of tracks we have processed (which should be 99)
def get_playlist_tracks(tracks,maxTracks,totalTracks,returnVal):

    print("loading existing playlist tracks...")
    results = sp.user_playlist_tracks(user=user_config['username'], playlist_id=playlistId, limit=99, offset=totalTracks)

    if len(results['items'])>0:
        #add the ids of the tracks we found to our track[] list, and increment the total tracks processed
        for result in results['items']:
            if returnVal=='id':
                item=result['track']['uri']
                item=item.split(':')[2]
                tracks.append(item)
                totalTracks+=1
            elif returnVal=='name':
                item=result['track']['name']
                item=cleanTitle(item,"(",")")
                item=cleanTitle(item,"[","]")
                tracks.append(item)
                totalTracks+=1
        return get_playlist_tracks(tracks,100,totalTracks,returnVal)

        #if our playlist contains no items (because it's a new playlist, or we processed them all),return our current tracklist (in the case of a new playlist, a blank list)

    elif len(results['items'])==None:
        print("error fetching playlist tracks or playlist is empty")
        tracks=[]
        return tracks

    elif len(results['items'])==0:
        print("all existing playlist tracks loaded")
        return tracks
    else:
        print("error fetching playlist tracks. warning: list may contain duplicates")
        return tracks


#
#add the batch to the playlist
def addSongsToPlaylist():
    print("adding tracks to playlist...")
    sp.user_playlist_add_tracks(user=user_config['username'], playlist_id=playlistId, tracks=trackids)
    print("success!")

#
#processes a batch, then terminates the program when all batches have processed


#
#spotify only allows us to return >100 items at a time. To get around this, we must split the songs into >100-song "batches"

#
#maxTitle is the maximum amount of titles spotify will allow us to search for at a time
#thisTitle counts how many files have been processed in this batch
#totalProcessed counts how many files have been processed altogether
#titleList will be our list of titles that have been found on Spotify and are ready to upload


def addBatch(totalProcessed,maxTitles,titlelist):

    print("adding batch...")

    #gets the current tracks in the playlist, in order to check for dups
    existing=[]
    if len(existing)!=len(titlelist):
        tracks=[]
        existing=get_playlist_tracks(tracks,100,0,'id')
    else:
        print("length of playlist equal to total item list")

    #number of titles processed this batch
    thisTitle=0

    #process the items in our trackList starting with the title after the last processed, and ending with the maximum allowed in a batch minus one(99)
    for item in range(totalProcessed,totalProcessed+maxTitles-1):

        #if we have not reached our batch limit and the titles processed is smaller than the number of titles in our title list
        if thisTitle<=maxTitles and totalProcessed<len(titlelist):

#
#before we can upload our tracks to a playlist, we need to grab their ids

            #try to get the trackid for our title
            try:
                print("{0} added to: {1} id: {3} {4!s} of {5!s} total: {6!s}".format(titlelist[item]['tracks']['items']['name'], playlistId, titlelist[item]['tracks']['items']['id'], thisTitle, maxTitles, totalProcessed))
                #print(titlelist[item]['tracks']['items']['name']+" added to "+playlistId+" id: "+titlelist[item]['tracks']['items']['id']+" "+str(thisTitle)+" of "+str(maxTitles)+" total: "+str(totalProcessed))
                titleid=titlelist[item]['tracks']['items']['id']
            #if the titleid isn't in our list of trackids, and it doesn't exist in our playlist, add it to the trackids and log it
                if titleid not in trackids and titleid not in existing:
                    trackids.append(titleid)
                    #write result to log
                    log.success(item,titlelist[item]['tracks']['items']['name'],titlelist[item]['tracks']['items']['id'])

            #if it is already in our list of track ids, skip it and log the result
                elif titleid in trackids:
                    print("skipping dup trackid...")
                    #write result to log
                    log.failure(item,titlelist[item]['tracks']['items']['name'],titlelist[item]['tracks']['items']['id'],'dup in trackid')

            #if it is already in our playlist, skip it and log the result
                elif titleid in existing:
                    print("track already added to playlist!")
                    #write result to log
                    log.failure(item,titlelist[item]['tracks']['items']['name'],titlelist[item]['tracks']['items']['id'],'track already added to playlist')

            #increment the ids processed this batch, and the total amount of ids processed
                thisTitle+=1
                totalProcessed+=1

            #if we couldn't get the track id from the track title for some reason, log the result
            except IndexError as e:
                print("couldn't add item! Error:{0!s}. Item:{1!s}".format(e,json.dumps(titlelist[item])))
                #write result to log
                log.failure(item,'unknown','unknown','couldn\'t add item')
            except Exception as e:
                print("titleList error:{0!s}".format(e))

        #exit the loop if we've reached our batch limit or reached the end of our list of titles
        else:
            break
#
#if our list of track ids is at least one, upload them to the playlist
    if len(trackids)>0:
        addSongsToPlaylist();
    else:
        print("no additional tracks to add")
#
#when the total processed is equal to the total number of items on our list of tracks, congratulations! we uploaded our list!
    if totalProcessed==len(titlelist):
        log.printLog()
        notFoundItems,failureItems,successItems=log.results()
        print(str(notFoundItems)+" items not found on Spotify, "+str(failureItems)+" items failed to upload and "+str(successItems)+" items added successfully!")
        print("(view log.txt for additional information)")
#
#if we still have some tracks on our tracklist, clear our list of track ids and start the next batch
    else:
        del trackids[:]
        #trackids.clear()
        addBatch(totalProcessed,maxTitles,titlelist)

if __name__ == '__main__':

#
#global variables

    playlistID = None
    user_config = {}
    ytList=[]
    trackids=[]
    skipList = "False"
    reload(sys)
    #sys.setdefaultencoding("utf-8")
    log = Log()

#load user credentials
    load_config()
    if user_config['username']=='' or user_config['client_id']=='' or user_config['client_secret']=='' or user_config['redirect_uri']=='':
        display_help(1)

#
#check arguments
    parser=argparse.ArgumentParser()
    parser.add_argument("--source","-s",help="the url of the youtube playlist we are creating out spotify list from. Can be set to \"data.txt\" to use a custom data.txt song list")
    parser.add_argument("--name","-n",help="an id for an existing playlist, a name of an existing playlist, a name for a new playlist, or blank--in which case a new playlist is created with the default name")
    parser.add_argument("--skipJSON","-skip",help="if set to True, a new JSON file will not be created and the last youtube playlist uploaded will be used",action="store_true")
    args = parser.parse_args()
#first argument checks for a URL, if none is present, a help message is displayed
    if args.source!=None:
        try:
            myURL=args.source
        except:
            print('an error occurred')
    elif args.source==None:
        print("error: a source url is required")
        display_help(2)
    
#second argument will be either:
#1 - an id for an existing playlist
#2 - a name of an existing playlist
#3 - a name for a new playlist
#4 - blank, in which case a new playlist is created with the default name
    if args.name!=None:
        try:        
            playlistId=args.name
            print("playlist id/name found")
        except:
            print('error: bad playlist id/name')
    elif args.name==None:
        playlistId=None
        print("creating new playlist")

#if the third argument is "True", skip creating the json 
    if args.skipJSON:
        skipList="True"
        print("skipping list creation")

    if myURL=='data.txt':
        skipList="True"
        print("skipping list creation, and using data.txt instead")


#create data.txt if none exists
    if os.path.exists('data.txt'):
        pass
    else:
        firstRun()

#create youtubeList, unless user chose to skiplist
    if skipList == "False":
        #build list
        print("trying to create youtube list...")
        ytList=getYoutube(myURL)
#
#connect to spotify
token = util.prompt_for_user_token(user_config['username'], scope='playlist-read-private,playlist-modify-private,playlist-modify-public', client_id=user_config['client_id'], client_secret=user_config['client_secret'], redirect_uri=user_config['redirect_uri'])

if token:
        sp = spotipy.Spotify(auth=token)
        print("connection successful")

#if token was successful, search for the songs in the list
        titlelist = findSongs()

#once we get our titlelist, add it to the batch
        addBatch(0,100,titlelist)
    

else:
        print ("Can't get token for", user_config['username'])