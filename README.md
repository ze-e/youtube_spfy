# youtube_spfy
Create a spotify playlist from a youtube playlist

CONFIGURING YOUTUBE_SPFY

Dependencies-- 

youtube-spfy takes the following dependencies:
python
https://www.python.org/downloads/
the youtube_dl python module
https://pypi.org/project/youtube_dl/

spotipy
https://spotipy.readthedocs.io/en/latest/

pyyaml
https://pyyaml.org/wiki/PyYAMLDocumentation

Configuration--

youtube_spfy must be configured before it can be used. You will need to enter a username, client_id, client_secret and redirect_uri, found in the config.yaml file

1.
The username is the userid of the account into which we are uploading our playlists. On mobile, it can be found by logging in, hitting the gear icon in the upper right hand corner of the app, and navigating to "Account". On desktop, it can be found by clicking on your username in the lower left hand corner, and clicking on "View Account," under the "Account Overview" tab.
```
===QUICK CONFIG===
you can configure your file with this default information. If so, skip number 2:
username: [your username]
client_id : "6496749177e54dcca460c2131d6fe77a"
client_secret : "dad3409cb96d457aa73f5b1550c3ebb8"
redirect_uri : "https://localhost:8080"
===         ====
```

2.
To create your config information:


The client_id, client_secret_, and redirect_uri are obtained by creating a developer account  and app at:
https://developer.spotify.com/dashboard/

Simply create an account, navigate to the dashboard and select "Create App." The client_id will be immediately available. To receive the client_secret, click "show client secret." To create a redirect_uri (https://localhost:8080 is fine), go to the app you created, and click on "edit settings," enter the redirect uri under "redirect uri," click "add," then click "save"

USING YOUTUBE_SPFY

To use youtube_spfy you must have spotify account to upload to, and the url of a youtube playlist. Simply enter youtube_spfy.py + the url + a name for the spotify playlist (optional) into the command line and hit enter!

You can also add the tracks from a youtube playlist into an existing spotify playlist by entering youtube_spfy.py + the url + the name or id of the spotify playlist

		1. create a new playlist from youtube URL:
		youtube_spfy.py [url]

		2.create a new playlist from youtube URL, with name [Name]
		youtube_spfy.py [url] [Name]

		3.add songs from youtube URL to existing Spotify playlist, with playlist id [Id] or name [Name]
		youtube_spfy.py [url] [Name/Id]

		4.skip json creation by adding \"true\". (Note: This will not work if you do not enter a name/ID!):
		youtube_spfy.py [url] [Name/Id][True]
    
The first time you use youtube_spfy, you will be asked to grant access to Spotify, and then redirected to your redirect uri. Simply copy the uri of the page you are redirected to (including the domain ie https://localhost:8080) into the command line and hit enter. You should not need to do this again unless your config.yaml file is edited or your token expires.

LOG.TXT

Sometimes youtube_spfy cannot find a song on Spotify, or an error occurs preventing a song from being uploaded to your list. Your Log.txt file will tell you exactly which songs failed because they could not be found on Spotify, which could not be uploaded due to an error, and which ones succeeded. If possible, it will include the name and/or Spotify id of the song.

Youtube_spfy will not allow duplicate files on a playlist. If a song was not added to the list because it was already found on the list, this will be stated on the log.txt entry for this song.

WE HOPE YOU ENJOY USING YOUTUBE SPFY!
