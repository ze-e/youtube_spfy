from __future__ import unicode_literals
import youtube_dl
import json
import sys
import spotipy
import yaml
import os
import spotipy.util as util
#used if you want to print json
from pprint import pprint

ytList={}
trackids=[]

def load_config():
    global user_config
    stream = open('config.yaml')
    user_config = yaml.load(stream)
    #pprint(user_config)

def firstRun():
	data={}
	with open('data.txt', 'w') as outfile:  
		json.dump(data, outfile)

#create json from youtube list
def getYoutube(url):

	print("building youtube json...")
	data = {}
	data['songs'] = []


	ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s%(ext)s','ignoreerrors': True})

	with ydl:
		result = ydl.extract_info(
		url,
		download=False # We just want to extract the info
		)

	if 'entries' in result:
	# Can be a playlist or a list of videos
		for video in result['entries']:
			if video!=None:
				video_title = video['title']
				data['songs'].append({
					'title' : video_title
				})

	else:
		# Just a video
		video = result
		video_title = video['title']
		print("title"+video_title)

		data['songs'].append({
			'title' : video_title
		})

	with open('data.txt', 'w') as outfile:  
		json.dump(data, outfile)

	with open('data.txt') as json_file:  
		data = json.load(json_file)
		for s in data['songs']:
			print(s['title'])
	return data

def sendList(list):
	print(ytList)

#search for songs
def getList():
	with open('data.txt') as json_file:  
		data = json.load(json_file)
	return data

def findSongs():
	global playlistId
	global log
	log['song_not_found'] = []

	maxTitles=100
	thisTitle=0
	totalProcessed=0
	titlelist=[]
	ytList=getList()
	print("building list...");
	for s in ytList['songs']:
		print(s['title'])
		result=sp.search(s['title'], limit=1, offset=0, type='track', market=None)
		#print("result"+str(result))
		if result not in titlelist and len(result['tracks']['items'])>0:
			print("--added to list...")
			titlelist.append(result)
		elif result in titlelist:
			print("--skipping dup track name...")
		elif len(result['tracks']['items'])==0:
			print("--song not found on spotify...")
			log['song_not_found'].append({
				'itemNumber' : s['title'],
				'result' :'song not found on spotify'
			})
	if playlistId == None:
		playlistId=createPlaylist()
	elif playlistId != None:
		playlistId=findExistingPlaylist()
	addNextBatch(totalProcessed,maxTitles,titlelist)

def createPlaylist():
	newList={}
	newList=sp.user_playlist_create(user=user_config['username'], name='youtube_spfy', public=True)
	newListId=newList['uri']
	newListId=newListId.split(':')[4]
	print("new playlist created! "+newListId)
	return newListId

def createPlaylist(playListName):
	newList={}
	newList=sp.user_playlist_create(user=user_config['username'], name=playListName, public=True)
	newListId=newList['uri']
	newListId=newListId.split(':')[4]
	print("new playlist created! "+newListId)
	return newListId

#getting tracks from an existing playlist
def get_playlist_tracks():
	#https://github.com/plamere/spotipy/issues/246
	tracks=[]
	maxTracks=100
	totalTracks=0
	while totalTracks<maxTracks:
		results = sp.user_playlist_tracks(user=user_config['username'],playlist_id=playlistId,limit=99,offset=totalTracks)
		#print("fetched playlist!"+str(totalTracks))
		try:
			working=results['items'][0]['track']['uri']
			pass
		except IndexError:
			#print(tracks)
			print("playlist empty!")
			return tracks
		for result in results['items']:
			item=result['track']['uri']
			item=item.split(':')[2]
			tracks.append(item)
			totalTracks+=1
	else:
		#print(tracks)
		return tracks

def findExistingPlaylist():
	playlists = sp.user_playlists(user=user_config['username'])
	for playlist in playlists['items']:
		if playlist['name']==playlistId:
			return playlist['id']
		elif playlist['id']==playlistId:
			return playlistId
		else:
			#raise NameError('Playlist id not found!')
			print("Could not find playlist name or id!")
			print("Creating new playlist!")
			newPlaylistId=createPlaylist(playlistId)
			return newPlaylistId


def addSongsToPlaylist():
	print("adding tracks to playlist...")
	sp.user_playlist_add_tracks(user=user_config['username'], playlist_id=playlistId, tracks=trackids)
	print("success!")

def addNextBatch(totalProcessed,maxTitles,titlelist):
	global log
	log['success'] = []
	log['failed'] = []
	print("adding next batch...")
	existing=[]
	if len(existing)!=len(titlelist):
		existing=get_playlist_tracks()
	else:
		print("length of playlist equal to total item list")
	thisTitle=0
	for item in range(totalProcessed,totalProcessed+maxTitles-1):
		if thisTitle<=maxTitles and totalProcessed<len(titlelist):
			try:
				print(titlelist[item]['tracks']['items'][0]['name']+" added to "+playlistId+" id: "+titlelist[item]['tracks']['items'][0]['id']+" "+str(thisTitle)+" of "+str(maxTitles)+" total: "+str(totalProcessed))
				titleid=titlelist[item]['tracks']['items'][0]['id']
				if titleid not in trackids and titleid not in existing:
					trackids.append(titleid)
					#write result to log
					log['success'].append({
						'itemNumber' : item,
						'title' : titlelist[item]['tracks']['items'][0]['name'],
						'id' : titlelist[item]['tracks']['items'][0]['id'],
						'result' :'added'
					})
				elif titleid in trackids:
					print("skipping dup trackid...")
					#write result to log
					log['failed'].append({
						'itemNumber' : item,
						'title' : titlelist[item]['tracks']['items'][0]['name'],
						'id' : titlelist[item]['tracks']['items'][0]['id'],
						'result' :'dup in trackid'
					})
				elif titleid in existing:
					print("track already added to playlist!")
					#write result to log
					log['failed'].append({
						'itemNumber' : item,
						'title' : titlelist[item]['tracks']['items'][0]['name'],
						'id' : titlelist[item]['tracks']['items'][0]['id'],
						'result' :'track already added to playlist'
					})
				thisTitle+=1
				totalProcessed+=1
			except IndexError:
				print("couldn't add item!")
				#write result to log
				log['failed'].append({
					'itemNumber' : item,
					'result' :'couldn\'t add item'
				})
		else:
			break
	if len(trackids)>0:
		addSongsToPlaylist();
	else:
		print("no tracks to add")

	if totalProcessed==len(titlelist):
		with open('log.txt', 'w') as outfile:  
			json.dump(log, outfile)
		print("successfully uploaded "+str(len(log['success']))+" files!")

	else:
		trackids.clear()
		addNextBatch(totalProcessed,maxTitles,titlelist)

if __name__ == '__main__':
	
	log={}
	global sp
	global user_config
	skipList = "False"
	load_config()
	#print("arguments:"+str(len(sys.argv)))
	#you must include a url to make the list from

	if len(sys.argv) > 1:
		try:
			myURL=sys.argv[1]
	#	except IndexError:
	#		print('no URL or missing arguments')
		except:
			print('an error occurred')
	elif len(sys.argv) == 1:
		text="""\
			WELCOME TO YOUTUBE_SPFY!

			How to use:

			1. create a new playlist from youtube URL:
			youtube_spfy.py [url]

			2.create a new playlist from youtube URL, with name [Name]
			youtube_spfy.py [url] [Name]

			3.add songs from youtube URL to existing Spotify playlist, with playlist id [Id] or name [Name]
			youtube_spfy.py [url] [Name/Id]

			4.skip json creation by adding \"true\". This will not work if you do not enter a name:
			youtube_spfy.py [url] [Name/Id][True]

			"""
		print(text)
		sys.exit()

	
	#add spotify playlist id as a third argument to use a new spfy playlist
	if len(sys.argv) > 2:
		try:		
			playlistId=sys.argv[2]
			print("using custom playlist id")
		except:
			print('error: bad playlist id')
	else:
		playlistId=None
		print("creating new playlist")

	#add "True" as a second argument to skip creating the json 
	if len(sys.argv) > 3:
		try:
			skipList=sys.argv[3]
			print("skipping list creation? "+str(skipList))
		except:
			print('please add argument 2, True or False')

	#create data.txt if none exists
	if os.path.exists('data.txt'):
		pass
	else:
		firstRun()

	#create youtubeList
	if skipList == "False":
		#build list
		print("trying to create youtube list...")
		ytList=getYoutube(myURL)
		sendList(ytList)

	#connect
token = util.prompt_for_user_token(user_config['username'], scope='playlist-modify-private,playlist-modify-public', client_id=user_config['client_id'], client_secret=user_config['client_secret'], redirect_uri=user_config['redirect_uri'])

if token:
        sp = spotipy.Spotify(auth=token)
        print("connection successful")

        #send list
        findSongs()
else:
        print ("Can't get token for", user_config['username'])

"""
To do: 
Fix broken logging (only logs last batch currently)
Add argparse (https://docs.python.org/3.3/library/argparse.html) to handle arguments
Improve search by parsing string, seperating track title and artist

to access desktop site:
'https://open.spotify.com/user/lpt1xrmg6nxefjj4rqksawj4d',
	
"""