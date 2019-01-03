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
    pprint(user_config)

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
	maxTitles=100
	thisTitle=0
	totalProcessed=0
	titlelist=[]
	ytList=getList()
	print("building list...");
	for s in ytList['songs']:
		print(s['title'])
		result=sp.search(s['title'], limit=1, offset=0, type='track', market=None)
		if result not in titlelist:
			titlelist.append(result)
		elif result in titlelist:
			print("skipping dup track name...")
	if playlistId == None:
		playlistId=createPlaylist()
	with open('newTitlelist.txt', 'w') as outfile:  
		json.dump(titlelist, outfile)
	addNextBatch(totalProcessed,maxTitles,titlelist)

def createPlaylist():
	newList={}
	newList=sp.user_playlist_create(user=user_config['username'], name='youtubeSync', public=True)
	newListId=newList['uri']
	newListId=newListId.split(':')[4]
	print("new playlist created! "+newListId)
	return newListId

#getting tracks from an existing playlist
def get_playlist_tracks():
	#.user_playlist(username, playlist_id,fields='tracks,next,name')
   """ results = sp.user_playlist_tracks(user=user_config['username'],playlist_id=playlistId)
    tracks = results['items'][0]['id']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'][0]['id'])
    return tracks"""
    results = sp.user_playlist_tracks(user=user_config['username'],playlist_id=playlistId)
    tracks = results['items'][0]['id']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'][0]['id'])
    return tracks
#def findExistingPlaylist():

def addSongsToPlaylist():
	print("adding tracks to playlist...")
	sp.user_playlist_add_tracks(user=user_config['username'], playlist_id=playlistId, tracks=trackids)
	print("success!")

def addNextBatch(totalProcessed,maxTitles,titlelist):
	print("adding next batch...")
	existing=get_playlist_tracks()
	thisTitle=0
	for item in range(totalProcessed,totalProcessed+maxTitles-1):
		if thisTitle<=maxTitles and totalProcessed<len(titlelist):
			try:
				print("Name "+titlelist[item]['tracks']['items'][0]['name']+" added to "+playlistId+" id: "+titlelist[item]['tracks']['items'][0]['id']+" "+str(thisTitle)+" of "+str(maxTitles)+" total: "+str(totalProcessed))
				titleid=titlelist[item]['tracks']['items'][0]['id']
				if titleid not in trackids and titleid not in existing:
					trackids.append(titleid)
				elif titleid in trackids:
					print("skipping dup trackid...")
				elif titleid in existing:
					print("track already added to playlist!")
				thisTitle+=1
				totalProcessed+=1
			except IndexError:
				print("couldn't add item!")
		else:
			break
	addSongsToPlaylist();

	if totalProcessed==len(titlelist):
		print("successfully uploaded "+str(totalProcessed)+" files!")
		existing=get_playlist_tracks()
		#pprint(existing)
		with open('newPlaylist.txt', 'w') as outfile:  
			json.dump(existing, outfile)
	else:
		trackids.clear()
		addNextBatch(totalProcessed,maxTitles,titlelist)
		#print("only run one batch")

if __name__ == '__main__':
	
	global sp
	global user_config
	skipList = "False"
	load_config()
	#print("arguments:"+str(len(sys.argv)))
	#you must include a url to make the list from
	try:
		myURL=sys.argv[1]
	except IndexError:
		print('no URL or missing arguments')
	except:
		print('an error occurred')

	#add "True" as a second argument to skip creating the json 
	if len(sys.argv) > 2:
		try:
			skipList=sys.argv[2]
			print("skipping list creation? "+str(skipList))
		except:
			print('please add argument 2, True or False')

	#add spotify playlist id as a third argument to use a new spfy playlist
	if len(sys.argv) > 3:
		try:		
			playlistId=sys.argv[3]
			print("using custom playlist id")
		except:
			print('error: bad playlist id')
	else:
		#playlistId=user_config['default_playlist_id']
		playlistId=None
		print("creating new playlist")

	if skipList == "False":
		#build list
		print("trying to create youtube list...")
		ytList=getYoutube(myURL)
		sendList(ytList)

	#create data.txt if none exists
	if os.path.exists('data.txt'):
		pass
	else:
		firstRun()

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
To do: fix duplicate problem
Fix adding to new list completing but not loading
Add argparse (https://docs.python.org/3.3/library/argparse.html) to handle arguments
Add naming list functionality


        
        {'collaborative': False, 

'description': None, 

'external_urls': {'spotify': 'https://open.spotify.com/playlist/0CraXC9lm477dQzKBoO2jV'}, 

'followers': {'href': None, 'total': 0}, 

'href': 'https://api.spotify.com/v1/playlists/0CraXC9lm477dQzKBoO2jV',
 'id': '0CraXC9lm477dQzKBoO2jV',
 'images': [],
 'name': 'youtubeSync', 
'owner': {'display_name': 'g3ngR', 'external_urls': 
		{'spotify': 'https://open.spotify.com/user/lpt1xrmg6nxefjj4rqksawj4d'},
	 'href': 'https://api.spotify.com/v1/users/lpt1xrmg6nxefjj4rqksawj4d', 
	'id': 'lpt1xrmg6nxefjj4rqksawj4d', 
	'type': 'user', 
	'uri': 'spotify:user:lpt1xrmg6nxefjj4rqksawj4d'}, 

'primary_color': None, 
'public': True, 
'snapshot_id': 'MSxjOWMwNmExMjFlODUzMzJiMjIxNjIzNGMzYzFkZTg3MDRkNDRhM2U4', 
'tracks': {'href': 'https://api.spotify.com/v1/playlists/0CraXC9lm477dQzKBoO2jV/tracks', 
	'items': [], 
	'limit': 100, 
	'next': None, 
	'offset': 0, 
	'previous': None, 
	'total': 0}, 

'type': 'playlist', 
'uri': 'spotify:user:lpt1xrmg6nxefjj4rqksawj4d:playlist:0CraXC9lm477dQzKBoO2jV'}
"""