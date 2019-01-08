# youtube_spfy
takes a youtube music list and creates a spotify playlist from it

CONFIGURING YOUTUBE_SPFY

Dependencies-- 
youtube-spfy takes the following dependencies:

the youtube_dl python module
#https://pypi.org/project/youtube_dl/

spotipy
#https://spotipy.readthedocs.io/en/latest/

pyyaml
https://pyyaml.org/wiki/PyYAMLDocumentation

Configuration--
youtube_spfy must be configured before it can be used. You will need to enter a username, client_id, client_secret and redirect_uri, found in the config.yaml file

1.
The username is the userid of the account into which we are uploading our playlists. On mobile, it can be found by logging in, hitting the gear icon in the upper right hand corner of the app, and navigating to "Account". On desktop, it can be found by clicking on your username in the lower left hand corner, and clicking on "View Account," under the "Account Overview" tab.

===QUICK CONFIG===
you can configure your file with this default information:
username: [your username]
client_id:"6496749177e54dcca460c2131d6fe77a"
client_secret:"dad3409cb96d457aa73f5b1550c3ebb8"
redirect_uri:"https://localhost:8080"
===         ====

Or, create your own config information:

2.
The client_id, client_secret_, and redirect_uri are obtained by creating a developer account  and app at:
https://developer.spotify.com/dashboard/

Simply create an account, navigate to the dashboard and select "Create App." The client_id will be immediately available. To receive the client_secret, click "show client secret." To create a redirect_uri (https://localhost:8080 is fine), go to the app you created, and click on "edit settings," enter the redirect uri under "redirect uri," click "add," then click "save"

USING YOUTUBE_SPFY
		1. create a new playlist from youtube URL:
		youtube_spfy.py [url]

		2.create a new playlist from youtube URL, with name [Name]
		youtube_spfy.py [url] [Name]

		3.add songs from youtube URL to existing Spotify playlist, with playlist id [Id] or name [Name]
		youtube_spfy.py [url] [Name/Id]

		4.skip json creation by adding \"true\". (Note: This will not work if you do not enter a name/ID!):
		youtube_spfy.py [url] [Name/Id][True]
    
The first time you use youtube_spfy, you will be asked to grant access to Spotify, and then redirected to your redirect uri. Simply copy the uri of the page you are redirected to (including the domain ie https://localhost:8080) into the command line and hit enter. You should not need to do this again unless your config.yaml file is edited or your token expires.

WE HOPE YOU ENJOY USING YOUTUBE SPFY!
