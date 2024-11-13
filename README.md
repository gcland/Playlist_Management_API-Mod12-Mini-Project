Playlist Management API

Welcome to Playlist Management API: A python Flask API project by Grant Copeland


First, you need to clone down the project using this command here:

    git clone git@github.com:gcland/Playlist_Management_API-Mod12-Mini-Project .git

Next, enter the following commands into the terminal:

    python3 -m venv myenv
    source myenv/bin/activate
    pip install flask sqlalchemy flask-sqlalchemy flask-marshmallow mysql-connector-python

Then, make sure your interpretter is in the virtual environment we just created:

> cmd + shift + p (mac)
> 	-> select virtual environment 

This project uses MySQL and Postman to operate the functions.
Start MySQL and enter the following command:

    CREATE DATABASE playlist_db;

This will create the database used within the python file.

Next, open the project folder. Within the 'password.py' file, enter your MySQL password. Save the file. 

Lastly, you will need to open Postman and create the requests. 
The navigate to the 'app.py' file, scroll to the endpoints (noted by '@app.route('{url}', methods=['{method}']).
Create each request in Postman per each endpoint in the Python 'app.py' file. 
For each request, select the appropriate method (GET/POST/PUT/DEL) per the endpoint. Then copy the url from the python code into the request URL.
Once all of the requests are set up per their respective endpoints, the project is ready to run.

Add songs:
- Begin by adding songs. You can either add songs individually or add a list of songs. Please see 'app.py' comments for formatting in Postman. Enter the information into the text body with the 'raw' radio-button selected.

From here, you can manage songs by updating a song's details, deleting a song, viewing all songs, viewing a song by ID, or viewing a song by title. 
Note: to use the view song by ID or view song by title you must follow the url format described within the python file at that endpoint.
Example url format for view song by title:

  http://127.0.0.1:5000/songs/by-title?title=

Above is the url for the endpoint to view songs by title. At the end of the url (after the '='), enter the name of the song; ex: http://127.0.0.1:5000/songs/by-title?title=Stairway to Heaven

Playlists:

Next you will want to add a playlist.
Begin by adding a playlist. Follow the format within 'app.py' to add a playlist. 
Ex: entry: 
{
    "name": "Playlist_Z",
    "songs": [1, 2]
}

Please note: duplicate songs cannot currently be added.

From here, you have the ability to:
- View all playlists
- View playlist by ID
- View playlist by Name
- View playlist songs by a criteria:
    - Enter the playlist name in the 'raw' text body and enter the criteria to search by into the url.
    - Ex:
    - (text body input) {
    "name": "Playlist_A"
      }
    - url: http://127.0.0.1:5000/sort_playlist_songs/by-criteria?criteria=genre
 
    - This will find Playlist_A and sort the songs by genre. A playlist can be sorted by song artists, genres, id's, or titles
    
- Update playlist: allows user to rewrite playlist name and list of songs
- Add song to playlist or remove a song from playlist:
  - Enter the playlist name into the url and song ID to add into the 'raw' text body.
  - Ex:
  - (text body input) {
    "id": 1
    }
  - url: http://127.0.0.1:5000/add_songID_playlist/by-name?name=Playlist_A 
  - This will add song ID: 1 to playlist A
  - Note: removing a song from playlist is a separate request and endpoint but is formatted the same as adding a song to playlist.
 
- Delete a playlist

Thank you for viewing this project! 

- Grant Copeland


