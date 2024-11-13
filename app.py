from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields, validate
from marshmallow import ValidationError
from sqlalchemy import select
from password import password

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://root:{password}@localhost/playlist_db' 
db = SQLAlchemy(app)
ma = Marshmallow(app)

class SongSchema(ma.Schema):
    title = fields.String(required=True)
    artist = fields.String(required=True)
    genre = fields.String(required=True)
    # could add album field

    class Meta:
        fields = ('id','title', 'artist', 'genre')

song_schema = SongSchema()
songs_schema = SongSchema(many=True)

class Song(db.Model):
    __tablename__ = 'Songs'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    artist = db.Column(db.String(255), nullable=False)
    genre = db.Column(db.String(255), nullable=False)

#Example format in Postman (add/update)

# {

#     "title":"XXXXXX",
#     "artist":"XXXXXX",
#     "genre":"XXXXXX",

# }

#Many to Many relationship - association table
playlist_song = db.Table('Playlist_Song',
    db.Column('playlist_id', db.Integer, db.ForeignKey('Playlists.id'), primary_key = True),
    db.Column('song_id', db.Integer, db.ForeignKey('Songs.id'), primary_key = True)
)

class Playlist(db.Model):
    __tablename__ = 'Playlists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    # customer_id = db.Column(db.Integer, db.ForeignKey('Customers.id'))
    songs = db.relationship('Song', secondary=playlist_song, backref=db.backref('playlists', lazy='dynamic'))

#Example format in Postman (add/update)
#{

    #"name": "XXXXXX"
    #"songs": [#, #]  Note: cannot have duplicate entries of song id's. quanity / duplicate song id's to come later

#}

class PlaylistSchema(ma.Schema):
    id = fields.Integer(required=False)
    name = fields.String(required=True)
    songs = fields.List(fields.Nested(SongSchema))

    class Meta:
        fields = ('id', 'name', 'songs')

playlist_schema = PlaylistSchema()
playlists_schema = PlaylistSchema(many=True)

# ---- Song endpoints ---- #

@app.route('/songs', methods=['GET'])
def get_songs():   # merge sort function sorts the list alphabetically using merge sort
    songs = Song.query.all()
    json_songs = songs_schema.jsonify(songs).json
    merge_sort(json_songs)
    return json_songs

@app.route('/songs/by-id', methods=['GET']) #/by-id?id=1    (example)
def view_by_songs_id():
    id = request.args.get('id')
    song = Song.query.filter(Song.id == id).first()
    if song:
        return song_schema.jsonify(song)
    else:
        return jsonify({"message": "Song not found"}), 404

@app.route('/songs/by-title', methods=['GET']) #/by-title?title="The Art of Coding" (example)
def view_by_song_title():
    title = request.args.get('title')
    json_songs = get_songs() # get_songs has merge_sort and sorts list before binary_search is executed
    song = binary_search(json_songs, title)
    if song:
        return song
    else:
        return jsonify({"message": "Song not found"}), 404

def binary_search(song_titles, title):
    low = 0 
    high = len(song_titles) - 1 
    success = False
    while low <= high:
        mid = (low+high)//2
        if ord(song_titles[mid]['title'][0]) == ord(title[0]):
            index = mid
            while ord(song_titles[index]['title'][0]) == ord(title[0]):
                try: 
                    song_titles[index]['title']
                    if song_titles[index]['title'] == title:
                        print(f'\nTitle: "{song_titles[index]['title']}" with id: {song_titles[index]['id']}.\n')
                        title = song_titles[index]['title']
                        id = song_titles[index]['id']
                        success = True
                        break
                    else:
                        index+=1
                except IndexError:
                    print(f"'{title}' was not found.")
                    break
            if success == True:
                return {'id': id, 'title': title}
            else:
                index = mid
                while ord(song_titles[index]['title'][0]) == ord(title[0]):
                    try: 
                        song_titles[index]['title']
                        if song_titles[index]['title'] == title:
                            print(f'\nTitle: "{song_titles[index]['title']}" with id: {song_titles[index]['id']}.\n')
                            title = song_titles[index]['title']
                            id = song_titles[index]['id']
                            success = True
                            break
                        else:
                            index-=1
                    except IndexError:
                        print(f"'{title}' was not found.")
                        break
                if success == True:
                    return {'id': id, 'title': title}
                else:
                    break
            
        elif ord(song_titles[mid]['title'][0]) < ord(title[0]):
            low = mid + 1
        else:
            high = mid - 1

@app.route('/song', methods=['POST'])
def add_song():
    try:
        song_data = song_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    new_song = Song(title=song_data['title'], artist=song_data['artist'], genre=song_data['genre'])
    db.session.add(new_song)
    db.session.commit()
    return jsonify({'message': 'New song added successfully'}), 201

@app.route('/songs', methods=['POST']) # see example postman format below this endpoint
def add_songs():
    try:
        json_songs = request.json
        songs_list = json_songs['songs']
        for song in songs_list: 
            new_song = Song(title=song['title'], artist=song['artist'], genre=song['genre'])
            db.session.add(new_song)
            db.session.commit()

    except ValidationError as err:
        return jsonify(err.messages), 400
    
    return jsonify({'message': 'New songs added successfully'}), 201    


# Example format input for inputting a list of songs
# {
#     "songs": [
#
#     {"title": "AAA", "artist": "111", "genre": "rock"},
#     {"title": "BBB", "artist": "222", "genre": "rap"}
#
# ]
# }

@app.route('/songs/<int:id>', methods=['PUT'])
def update_song(id):
    song = Song.query.get_or_404(id)
    try:
        song_data = song_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    song.title = song_data['title']
    song.artist = song_data['artist']
    song.genre = song_data['genre']
    db.session.commit()
    return jsonify({'message':'Song details updated successfully'}), 200

@app.route('/songs/<int:id>', methods=['DELETE'])
def delete_song(id):
    song = Song.query.get_or_404(id)
    db.session.delete(song)
    db.session.commit()
    return jsonify({'message':'Song removed successfully'}), 200

# ---- Playlist endpoints ---- #

@app.route('/playlists', methods=['GET'])
def get_playlists():
    playlists = Playlist.query.all()
    json_playlists = playlists_schema.jsonify(playlists).json
    # merge_sort(json_playlists)
    return json_playlists


@app.route('/playlists', methods=['POST']) 
def add_playlist():
    try:
        json_playlist = request.json
        songs = json_playlist.pop('songs', [])
        if not songs:
            songs = []
        playlist_data = playlist_schema.load(json_playlist)
    except ValidationError as err:
        return jsonify(err.messages), 400

    new_playlist = Playlist(name=playlist_data['name'])
    for song in songs:
        item = Song.query.filter_by(id = song).first()
        new_playlist.songs.append(item)
    db.session.add(new_playlist)
    db.session.commit()
    return jsonify({'message': 'New playlist created successfully'}), 201    

@app.route('/playlists/<int:playlist_id>', methods=['PUT']) 
def update_playlist(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)
    try:
        json_playlist = request.json
        print(json_playlist)
        songs = json_playlist.pop('songs', [])
        if not songs:
            return jsonify({'Error': 'cannot update playlist without songs.'}), 400
        playlist_data = playlist_schema.load(request.json)
        print(playlist_data)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    playlist.name = playlist_data['name']
    playlist.songs.clear()
    for song in songs:
        item = Song.query.filter_by(id = song).first()
        playlist.songs.append(item)
    print(playlist, playlist.songs)
    print(playlist_data)
    db.session.commit()
    return jsonify({'message':'Playlist details updated successfully'}), 200

@app.route('/add_songID_playlist/by-name', methods=['PUT']) #/by-name?name="AAA" (example) 
# playlist name goes in search bar, song is added by id in raw input (postman). 
# Example input: { "id": 4 } Note: the value for "id" can be int or str; Example input: { "id": 4 } or { "id": "4" }
def add_songID_playlist():
    try:
        playlist = (view_by_playlist_name()) # uses merge_sort and binary_search
        id = playlist['id']
        playlist_obj = Playlist.query.filter(Playlist.id == id).first()
    except ValidationError as err:
        return jsonify(err.messages), 400
    songs = playlist['songs']
    songsList = []
    for song in songs:
        id = song['id']
        song = Song.query.filter(Song.id == id).first()
        songsList.append(song)
    json_songToAdd = request.json
    print('Song to add:', json_songToAdd)
    if json_songToAdd['id']:
        id = json_songToAdd['id']
        song = Song.query.filter(Song.id == id).first()
        if song:
            songsList.append(song)
    playlist_obj.songs = songsList
    db.session.commit()
    return jsonify({'message':f'Playlist song: {json_songToAdd} added successfully'}), 200

@app.route('/remove_songID_playlist/by-name', methods=['PUT']) #/by-name?name="AAA" (example) 
# playlist name goes in search bar, song is removed by id in raw input (postman). 
# Example input: { "id": 4 } Note: the value for "id" can be int or str; Example input: { "id": 4 } or { "id": "4" }
def remove_songID_playlist():
    try:
        playlist = (view_by_playlist_name()) # uses merge_sort and binary_search
        id = playlist['id']
        playlist_obj = Playlist.query.filter(Playlist.id == id).first()
        print(playlist_obj)
    except ValidationError as err:
        return jsonify(err.messages), 400
    songs = playlist_obj.songs
    print(songs)
    songIDList = []
    for song in playlist['songs']:
        songIDList.append(song['id'])
    json_songToRemove = request.json
    print('Song to remove:', json_songToRemove['id'])
    search = binary_search_ID(songIDList, json_songToRemove['id'])
    songs.pop(search['index'])
    db.session.commit()
    return jsonify({'message':f'Playlist song: {json_songToRemove} removed successfully'}), 200

@app.route('/playlists/<int:playlist_id>', methods=['DELETE'])
def delete_playlist(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)
    db.session.delete(playlist)
    db.session.commit()
    return jsonify({'message':'Playlist removed successfully'}), 200

@app.route('/playlists/by-id', methods=['GET']) #/by-id?id=1    (example)
def view_by_playlist_id():
    id = request.args.get('id')
    playlist = Playlist.query.filter(Playlist.id == id).first()
    if playlist:
        return playlist_schema.jsonify(playlist)
    else:
        return jsonify({"message": "Playlist not found"}), 404
    
@app.route('/playlists/by-name', methods=['GET']) #/by-name?name="AAA" (example)
def view_by_playlist_name():
    name = request.args.get('name')
    json_playlists = get_playlists()
    merge_sort_criteria(json_playlists, 'name')     # sorts playlists by name before executing binary search
    playlist = binary_search_playlist(json_playlists, name)
    if playlist:
        return playlist
    else:
        return jsonify({"message": "Playlist not found"}), 404

@app.route('/sort_playlist_songs/by-criteria', methods=['GET']) #/by-name?name="AAA" (example)
def view_playlistSongs_by_criteria():
    criteria = request.args.get('criteria')
    json_playlists = get_playlists()
    json_name = request.json
    playlist = binary_search_playlist(json_playlists, json_name['name'])
    if playlist:
        list = playlist['songs']
        list = merge_sort_criteria(list, criteria)
        playlist['songs'] = list 
        return playlist
    else:
        return jsonify({"message": "Playlist not found"}), 404

def binary_search_playlist(playlist_list, name):
    low = 0 
    high = len(playlist_list) - 1 
    success = False
    while low <= high:
        mid = (low+high)//2
        if ord(playlist_list[mid]['name'][0]) == ord(name[0]):
            index = mid
            while ord(playlist_list[index]['name'][0]) == ord(name[0]):
                try: 
                    playlist_list[index]['name']
                    if playlist_list[index]['name'] == name:
                        print(f'\nName: "{playlist_list[index]['name']}" with id: {playlist_list[index]['id']}.\n')
                        name = playlist_list[index]['name']
                        id = playlist_list[index]['id']
                        songs = playlist_list[index]['songs']
                        success = True
                        break
                    else:
                        index+=1
                except IndexError:
                    print(f"'{name}' was not found.")
                    break
            if success == True:
                return {'id': id, 'name': name, 'songs': songs}
            else:
                index = mid
                while ord(playlist_list[index]['name'][0]) == ord(name[0]):
                    try: 
                        playlist_list[index]['name']
                        if playlist_list[index]['name'] == name:
                            print(f'\nName: "{playlist_list[index]['name']}" with id: {playlist_list[index]['id']}.\n')
                            name = playlist_list[index]['name']
                            id = playlist_list[index]['id']
                            success = True
                            break
                        else:
                            index-=1
                    except IndexError:
                        print(f"'{name}' was not found.")
                        break
                if success == True:
                    return {'id': id, 'name': name}
                else:
                    break
            
        elif ord(playlist_list[mid]['name'][0]) < ord(name[0]):
            low = mid + 1
        else:
            high = mid - 1

def binary_search_ID(songs, id):
    # print(songs)
    # merge_sort_criteria(songs, 'id')
    # print(songs)
    low = 0 
    high = len(songs) - 1 
    success = False
    while low <= high:
        mid = (low+high)//2
        if songs[mid] == id:
            index = mid
            while songs[mid] == id:
                try: 
                    songs[index]
                    if songs[index] == id:
                        print(f'\nSong ID: {songs[index]}; index: {index}.\n')
                        id = songs[index]
                        success = True
                        break
                    else:
                        index+=1
                except IndexError:
                    print(f"'{id}' was not found.")
                    break
            if success == True:
                return {'id': id, 'index': index}
            else:
                index = mid
                while songs[index] == id:
                    try: 
                        songs[index]
                        if songs[index] == id:
                            print(f'\nSong ID: {songs[index]}; index: {index}.\n')
                            id = songs[index]
                            success = True
                            break
                        else:
                            index+=1
                    except IndexError:
                        print(f"'{id}' was not found.")
                        break
                if success == True:
                    return {'id': id, 'index': index}
                else:
                    break
            
        elif songs[mid] < id:
            low = mid + 1
        else:
            high = mid - 1

def merge_sort(list):
    if len(list) > 1:
        mid = len(list)//2
        left_half = list[:mid]
        right_half = list[mid:]

        merge_sort(left_half)
        merge_sort(right_half)

        i = j = k = 0

        while i < len(left_half) and j < len(right_half):
            if left_half[i]['title'] < right_half[j]['title']:
                list[k] = left_half[i]
                i+=1

            else:
                list[k] = right_half[j]
                j+=1
            k+=1
        while i < len(left_half):
            list[k] = left_half[i]
            i+=1
            k+=1
        
        while j < len(right_half):
            list[k] = right_half[j]
            j+=1
            k+=1
    return list

def merge_sort_criteria(list, criteria):
    if len(list) > 1:
        mid = len(list)//2
        left_half = list[:mid]
        right_half = list[mid:]

        merge_sort_criteria(left_half, criteria)
        merge_sort_criteria(right_half, criteria)

        i = j = k = 0

        while i < len(left_half) and j < len(right_half):
            if left_half[i][criteria] < right_half[j][criteria]:
                list[k] = left_half[i]
                i+=1

            else:
                list[k] = right_half[j]
                j+=1
            k+=1
        while i < len(left_half):
            list[k] = left_half[i]
            i+=1
            k+=1
        
        while j < len(right_half):
            list[k] = right_half[j]
            j+=1
            k+=1
    return list

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)

