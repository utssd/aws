"""
Doc.

Doc.
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import render_template
import datetime



app = Flask(__name__)

# for test purposes, use sqlite:////path/test.db instead
# a config file is needed
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://utssd:<CS>demima888!@banddb.cybt0ykhyacv.us-west-2.rds.amazonaws.com:5432/banddb"

db = SQLAlchemy(app)

# *************
# Tips to Note
# *************
# Integer PK will autoincrement by default in Flask SQLAlchemy
# Table name is automatically generated in F-S as "CamelCase" to "camel_case"
# Use append() to insert one-to-many and many-to-many relations
# connections are automatically closed
# *************

TopSongs = db.Table('top_songs',
                    db.Column('ArtistID', db.Integer,
                              db.ForeignKey('artists.ArtistID')),
                    db.Column('SongID', db.Integer, db.ForeignKey('songs.SongID')))

ArtistGenre = db.Table('artist_genre',
                       db.Column('ArtistID', db.Integer,
                                 db.ForeignKey('artists.ArtistID')),
                       db.Column('GID', db.Integer, db.ForeignKey('genre.GID')))

SongGenre = db.Table('song_genre',
                     db.Column('SongID', db.Integer,
                               db.ForeignKey('songs.SongID')),
                     db.Column('GID', db.Integer, db.ForeignKey('genre.GID')))

AlbumGenre = db.Table('album_genre',
                      db.Column('AlbumID', db.Integer,
                                db.ForeignKey('albums.AlbumID')),
                      db.Column('GID', db.Integer, db.ForeignKey('genre.GID')))

TourLineUp = db.Table('tour_line_up',
                      db.Column('TourID', db.Integer,
                                db.ForeignKey('tours.TourID')),
                      db.Column('SongID', db.Integer, db.ForeignKey('songs.SongID')))


class Artists(db.Model):
    """
    Model Artists:
    features of ArtistID, Name, Start_Time, End_Time,
    relations to Songs, Albums, Tours,
    relations of top_3_songs (a table), genre (a table)
    """

    ArtistID = db.Column(db.Integer, nullable=False, primary_key=True)
    Name = db.Column(db.String, nullable=False)
    Age = db.Column(db.Integer, nullable=True)
    Origin = db.Column(db.String, nullable=True)
    Start_Time = db.Column(db.Date, nullable=True)
    End_Time = db.Column(db.Date, nullable=True)
    Image = db.Column(db.String, nullable=True)

#   top 3 songs are many-to-many relationship
    TopSongs = db.relationship(
        'Songs', secondary=TopSongs, backref=db.backref('a', lazy='dynamic'))

#   Artist-genre is a many-to-many relationship
    ArtistGenre = db.relationship('Genre', secondary=ArtistGenre, backref=db.backref(
        'artist', lazy='dynamic'))

#   artist-song is a one-to-many relationship
    Songs = db.relationship('Songs', backref='artist', lazy='dynamic')

#   artist-album is a one-to-many relationship
    Albums = db.relationship('Albums', backref='artist', lazy='dynamic')

#   artist-tour is a one-to-many relationship
    Tours = db.relationship('Tours', backref='artist', lazy='dynamic')

    def __init__(self, name, image, start_time=None, age=None, origin=None, end_time=None, **rest):
        self.Name = name
        self.Start_Time = start_time
        self.End_Time = end_time
        self.Age = age
        self.Origin = origin
        self.Image = image

    def __repr__(self):
        return self.Name


class Songs(db.Model):
    """
    Model Songs:
    features of SongID, Name, Creation_Date, Chart_Position, Run_Time
    relations from Artists, Albums, Labels
    relations of genre (a table)
    """
    SongID = db.Column(db.Integer,  nullable=False, primary_key=True)
    Name = db.Column(db.String, nullable=False)
    Creation_Date = db.Column(db.Date, nullable=False)
    Chart_Position = db.Column(db.Integer, nullable=True)
    Run_Time = db.Column(db.Integer, nullable=False)
    Image = db.Column(db.String, nullable=True)

#   song-genre is a many-to-many relationship
    SongGenre = db.relationship('Genre', secondary=SongGenre, backref=db.backref(
        'song', lazy='dynamic'))

#   artist-song is a one-to-many relationship
    ArtistID = db.Column(db.Integer, db.ForeignKey("artists.ArtistID"))

#   album-song is a one-to-many relationship
    AlbumID = db.Column(db.Integer, db.ForeignKey('albums.AlbumID'))

#   label-song is a one-to-many relationship
    LabelID = db.Column(db.Integer, db.ForeignKey("labels.LabelID"))

    def __init__(self, name, creation_date, run_time, image, chart_position=None, **rest):
        self.Name = name
        self.Creation_Date = creation_date
        self.Chart_Position = chart_position
        self.Run_Time = run_time
        self.Image = image

    def __repr__(self):
        return self.Name


class Albums(db.Model):
    """
    Model Albums has
    features of AlbumID, Title, Year, US_Chart_Position
    relations from Labels, Artists,
    relations to Songs
    relations of genre (album_genre, a table)
    """
    AlbumID = db.Column(db.Integer, nullable=False, primary_key=True)
    Title = db.Column(db.String, nullable=False)
    Year = db.Column(db.Date, nullable=True)
    US_Chart_Postion = db.Column(db.Integer, nullable=True)
    Image = db.Column(db.String, nullable=True)

#   Album-song is a one-to-many relationship
    LabelID = db.Column(db.Integer, db.ForeignKey(
        "labels.LabelID"), nullable=True)
#   Artist-album is a one-to-many relationship
    ArtistID = db.Column(db.Integer, db.ForeignKey(
        "artists.ArtistID"), nullable=True)
#   Album-song is a one-to-many relationship
    Songs = db.relationship('Songs', backref='album')

    AlbumGenre = db.relationship('Genre', secondary=AlbumGenre, backref=db.backref(
        'album', lazy='dynamic'))

    def __init__(self, title, year, image, us_chart_position=None, **rest):
        self.Title = title
        self.Year = year
        self.US_Chart_Postion = us_chart_position
        self.Image = image

    def __repr__(self):
        return self.Title


class Tours(db.Model):
    """
    Model Tours has
    features of TourID, Venue, Location, tDate,
    relations from Artist
    relations of tour_line_up (a table)
    """
    TourID = db.Column(db.Integer, nullable=False, primary_key=True)
    Venue = db.Column(db.String, nullable=False)
    Location = db.Column(db.Integer, nullable=False)
    tDate = db.Column(db.Date, nullable=False)
    Image = db.Column(db.String, nullable=True)

#   Artist-tour is a one-to-many relationship
    ArtistID = db.Column(db.Integer, db.ForeignKey(
        "artists.ArtistID"), nullable=False)
#   Tour-tour_line_up is a many to many relationship
    TourLineUp = db.relationship('Songs', secondary=TourLineUp, backref=db.backref(
        'tour', lazy='dynamic'))

    def __init__(self, venue, location, date, **rest):
        self.Venue = venue
        self.Location = location
        self.tDate = date
        self.Image = image


class Genre(db.Model):
    """
    Model Genre has
    feature of GID, Name
    relations of song_genre (a table), album_genre (a table)
    """
    GID = db.Column(db.Integer, nullable=False, primary_key=True)
    Name = db.Column(db.String, nullable=False)
    Image = db.Column(db.String, nullable=True)

    def __init__(self, name, image=None):
        self.Name = name
        self.Image = image

    def __repr__(self):
        return self.Name


class Labels(db.Model):
    """
    Model Labels has
    features of LabelID, Name
    relations to Albums, Songs
    """
    LabelID = db.Column(db.Integer, nullable=False, primary_key=True)
    Name = db.Column(db.String, nullable=False)
    Image = db.Column(db.String, nullable=True)

#   one-to-many
    Albums = db.relationship('Albums', backref='label', lazy='dynamic')

#   one-to-many
    Songs = db.relationship('Songs', backref='label', lazy='dynamic')

    def __init__(self, name, image=None):
        self.Name = name
        self.Image = image

    def __repr__(self):
        return self.Name

from sqlalchemy import func


class dbQuery:
    """
    all query functions
    """

    def AllArtists(self, sorting):
        if sorting == 'desc':
            artists = Artists.query.order_by(
                (db.func.lower(Artists.Name)).desc()).all()
            for a in artists:
                a.ArtistGenre
            artistsInfo = [a.__dict__ for a in artists]
        else:
            artists = Artists.query.order_by(
                (db.func.lower(Artists.Name)).asc()).all()
            for a in artists:
                a.ArtistGenre
            artistsInfo = [a.__dict__ for a in artists]
        return artistsInfo  # return a list of dict of artist

    def ArtistByName(self, name):
        artists = Artists.query.filter(Artists.Name == name).all()
        for a in artists:
            a.ArtistGenre
        artistsInfo = [a.__dict__ for a in artists]
        return artistsInfo  # return a list of dict of artist

    def ArtistByID(self, ID):
        artists = Artists.query.filter(Artists.ArtistID == ID).first()
        artists.ArtistGenre
        artistsInfo = artists.__dict__
        return artistsInfo

    def ArtistGenre(self, artist):
        genre = Artists.query.filter(
            Artists.Name == artist).first().ArtistGenre
        return genre  # return a list

    def ArtistByGenre(self, genre, sorting):
        if sorting == 'desc':
            artists = Artists.query.filter(Artists.ArtistGenre.any(Name=genre)).order_by(
                (db.func.lower(Artists.Name)).desc()).all()
            for a in artists:
                a.ArtistGenre
            artistsInfo = [a.__dict__ for a in artists]
        else:
            artists = Artists.query.filter(Artists.ArtistGenre.any(Name=genre)).order_by(
                (db.func.lower(Artists.Name)).asc()).all()
            for a in artists:
                a.ArtistGenre
            artistsInfo = [a.__dict__ for a in artists]
        return artistsInfo

    def ArtistSongs(self, artist):
        songs = Songs.query.join(Artists).filter(Artists.Name == artist).all()
        songsInfo = [s.__dict__ for s in songs]
        return songsInfo

    def ArtistImage(self, artist):
        return Artists.query.filter(Artists.Name == artist).first().Image

    def GetArtist(self, artist):
        a = Artists.query.filter(Artists.Name == artist).first()
        a.ArtistGenre
        return a.__dict__

    def AllSongs(self, sorting):
        if sorting == 'desc':
            songs = Songs.query.order_by(
                (db.func.lower(Songs.Name)).desc()).all()
            for s in songs:
                s.SongGenre
            songsInfo = [s.__dict__ for s in songs]
        else:
            songs = Songs.query.order_by(
                (db.func.lower(Songs.Name)).asc()).all()
            for s in songs:
                s.SongGenre
            songsInfo = [s.__dict__ for s in songs]
        return songsInfo

    def SongByID(self, ID):
        songs = Songs.query.filter(Songs.SongID == ID).first()
        songs.SongGenre
        songsInfo = songs.__dict__
        return songsInfo


    def SongAlbum(self, song):
        albums = Albums.query.join(Songs).filter(Songs.Name == song).all()
        albumsInfo = [al.__dict__ for al in albums]
        return albumsInfo

    def SongByGenre(self, genre, sorting):
        if sorting == 'desc':
            songs = Songs.query.filter(Songs.SongGenre.any(Name=genre)).order_by(
                (db.func.lower(Songs.Name)).desc()).all()
            for s in songs:
                s.SongGenre
            songsInfo = [s.__dict__ for s in songs]
        else:
            songs = Songs.query.filter(Songs.SongGenre.any(Name=genre)).order_by(
                (db.func.lower(Songs.Name)).desc()).all()
            for s in songs:
                s.SongGenre
            songsInfo = [s.__dict__ for s in songs]
        return songsInfo

    def SongByAlbum(self, album):
        songs = Songs.query.join(Albums).filter(Albums.Title == album).all()
        for s in songs:
            s.SongGenre
        songsInfo = [s.__dict__ for s in songs]
        return songsInfo

    def SongImage(self, song):
        return Songs.query.filter(Songs.Name == song).first().Image

    def GetSong(self, song):
        a = Songs.query.filter(Songs.Name == song).first()
        a.SongGenre
        return a.__dict__

    def AllAlbums(self, sorting):
        if sorting == 'desc':
            albums = Albums.query.order_by(
                (db.func.lower(Albums.Title)).desc()).all()
            albumsInfo = [al.__dict__ for al in albums]
        else:
            albums = Albums.query.order_by(
                (db.func.lower(Albums.Title)).asc()).all()
            albumsInfo = [al.__dict__ for al in albums]
        return albumsInfo

    def AlbumByID(self, ID):
        albums = Albums.query.filter(Albums.AlbumID == ID).first()
        albumsInfo = albums.__dict__
        return albumsInfo


    def AlbumByArtist(self, artist):
        albums = Albums.query.join(Artists).filter(
            Artists.Name == artist).all()
        albumsInfo = [al.__dict__ for al in albums]
        return albumsInfo

    def AlbumImage(self, album):
        return Albums.query.filter(Albums.Title == album).first().Image

    def GetAlbum(self, album):
        a = Albums.query.filter(Albums.Title == album).first()
        aInfo = a.__dict__
        return aInfo

    def AllGenre(self):
        genre = Genre.query.all()
        genreInfo = [g.__dict__ for g in genre]
        return genreInfo

    def SortArtistAsc(self):
        artists = Artists.query.order_by(
            (db.func.lower(Artists.Name)).asc()).all()
        for a in artists:
            a.ArtistGenre
        artistsInfo = [a.__dict__ for a in artists]
        return artistsInfo

    def SortArtistDes(self):
        artists = Artists.query.order_by(
            (db.func.lower(Artists.Name)).desc()).all()
        for a in artists:
            a.ArtistGenre
        artistsInfo = [a.__dict__ for a in artists]
        return artistsInfo

    def SortSongAsc(self):
        songs = Songs.query.order_by((db.func.lower(Songs.Name)).asc()).all()
        for s in songs:
            s.SongGenre
        songsInfo = [s.__dict__ for s in songs]
        return songsInfo

    def SortSongDes(self):
        songs = Songs.query.order_by((db.func.lower(Songs.Name)).desc()).all()
        for s in songs:
            s.SongGenre
        songsInfo = [s.__dict__ for s in songs]
        return songsInfo

    def SortAlbumAsc(self):
        albums = Albums.query.order_by(
            (db.func.lower(Albums.Title)).asc()).all()
        albumsInfo = [al.__dict__ for al in albums]
        return albumsInfo

    def SortAlbumDes(self):
        albums = Albums.query.order_by(
            (db.func.lower(Albums.Title)).desc()).all()
        albumsInfo = [al.__dict__ for al in albums]
        return albumsInfo




import flask_restless

# Create the Flask-Restless API manager.
manager = flask_restless.APIManager(app, flask_sqlalchemy_db=db)

# Create API endpoints, which will be available at /api/<tablename> by
# default. Allowed HTTP methods can be specified as well.
manager.create_api(Artists, methods=['GET'])
manager.create_api(Songs, methods=['GET'])
manager.create_api(Albums, methods=['GET'])
manager.create_api(Genre, methods=['GET'])


@app.route('/')
@app.route('/index')
def index():
    """
    Doc.

    Doc.
    """
    return render_template('index.html')


@app.route('/artist/<path:artist_name>')  # when does this get called?
def artist(artist_name):
    """
    Doc.

    Doc.
    """
    artist_name = str(artist_name.replace('%20', ' '))
    a = dbQuery().GetArtist(artist_name)
    s = dbQuery().ArtistSongs(artist_name)
    al = dbQuery().AlbumByArtist(artist_name)
    return render_template('artist-info.html', artist=a, songs=s, albums=al)


@app.route('/artists', defaults={'sorting': 'asc', 'page': 1}, strict_slashes=False)
@app.route('/artists/<string:sorting>/<int:page>')
def artists(sorting, page):
    """
    Doc.

    Doc.
    """
    data = dbQuery().AllArtists(sorting)
    pages = len(data)
    data = data[(page - 1) * 8: page * 8]
    return render_template('artists.html', data=data, genre='',sorting=sorting,pages=pages, language='Python', framework='Flask', lang=False)


@app.route('/artists_by_genre/<string:genre>/<string:sorting>/<int:page>')
def artists_by_genre(genre, sorting, page):
    data = dbQuery().ArtistByGenre(genre, sorting)
    pages = len(data)
    data = data[(page - 1) * 8: page * 8]
    return render_template('artists.html', data=data, pages=pages, genre=genre, sorting=sorting,language='Python', framework='Flask', lang=False)


@app.route('/albums/<string:album_name>')
def album(album_name):
    album_name = str(album_name.replace('%20', ' '))
    a = dbQuery().GetAlbum(album_name)
    s = dbQuery().SongByAlbum(album_name)
    ar = dbQuery().ArtistByID(a['ArtistID'])
    return render_template('album-info.html', album=a, songs=s, artist=ar)


@app.route('/albums', defaults={'sorting': 'asc', 'page': 1}, strict_slashes=False)
@app.route('/albums/<string:sorting>/<int:page>')
def albums(sorting, page):
    """
    Doc.

    Doc.
    """
    data = dbQuery().AllAlbums(sorting)
    pages = len(data)
    data = data[(page - 1) * 8: page * 8]
    return render_template('albums.html', data=data, pages=pages, sorting=sorting,language='Python', framework='Flask', lang=False)


@app.route('/tours')
def tours():
    """
    Doc.

    Doc.
    """
    return render_template('tours.html')


@app.route('/songs/<song_name>')
def song(song_name):
    song_name = str(song_name.replace('%20', ' '))
    s = dbQuery().GetSong(song_name)
    ar = dbQuery().ArtistByID(s['ArtistID'])
    al = dbQuery().AlbumByID(s['AlbumID'])
    return render_template('song-info.html', song=s, album=al, artist=ar)


@app.route('/songs', defaults={'sorting': 'asc', 'page': 1}, strict_slashes=False)
@app.route('/songs/<string:sorting>/<int:page>')
def songs(sorting, page):
    """
    Doc.

    Doc.
    """
    data = dbQuery().AllSongs(sorting)
    pages = len(data)
    data = data[(page - 1) * 8: page * 8]
    return render_template('songs.html', data=data, pages=pages, sorting=sorting,language='Python', framework='Flask', lang=False)


@app.route('/songs_by_genre/<string:genre>/<string:sorting>/<int:page>')
def songs_by_genre(genre, sorting, page):
    data = dbQuery().SongByGenre(genre, sorting)
    pages = len(data)
    data = data[(page - 1) * 8: page * 8]
    return render_template('songs.html', data=data, pages=pages, genre=genre, sorting=sorting,language='Python', framework='Flask', lang=False)


@app.route('/about')
def about():
    """
    Doc.

    Doc.
    """
    return render_template('about.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.teardown_request
def teardown_request(exception):
    if exception:
        db.session.rollback()
        db.session.remove()
    db.session.remove()

