"""
Doc.

Doc.
"""
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask import render_template
from flask_cors import CORS
from flask_recaptcha import ReCaptcha
import datetime

app = Flask(__name__)
recaptcha = ReCaptcha(app=app, site_key='6Let5SgUAAAAADOF-hAru-JurTkgEI8Heb6evOcL', secret_key='6Let5SgUAAAAAKrafblaBR2gED50MPLlFFTclfn0')


# for test purposes, use sqlite:////path/test.db instead
# a config file is needed
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://utssd:<CS>demima888!@banddb.cybt0ykhyacv.us-west-2.rds.amazonaws.com:5432/banddb"

CORS(app, headers=['Content-Type'])


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
    US_Chart_Position = db.Column(db.Integer, nullable=True)
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
        self.US_Chart_Position = us_chart_position
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
    tDate = db.Column(db.String, nullable=False)
    Name = db.Column(db.String, nullable=False)
    Image = db.Column(db.String, nullable=True)
    Venue = db.Column(db.String, nullable=False)
    Locations = db.Column(db.String, nullable=False)

#   Artist-tour is a one-to-many relationship
    ArtistID = db.Column(db.Integer, db.ForeignKey(
        "artists.ArtistID"), nullable=True)
#   Tour-tour_line_up is a many to many relationship
    TourLineUp = db.relationship('Songs', secondary=TourLineUp, backref=db.backref(
        'tour', lazy='dynamic'))

    def __init__(self, date, name, image, venue, locations, **rest):
        self.tDate = date
        self.Name = name
        self.Image = image
        self.Venue = venue
        self.Locations = locations

    def __repr__(self):
        return self.Name


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



# utility functions
def getDate(s, f="%d %b %Y, %H:%M"):
    return datetime.datetime.strptime(s, f).date().isoformat()

def getRunTime(s):
    return int(s) // 1000


@app.route('/edit/<string:_type>/<int:_id>/', methods=['GET', 'POST'], strict_slashes=False)
def edit(_type, _id):
    if request.method == 'GET':
        artists = [tuple((a.Name, a.ArtistID)) for a in Artists.query.all()]
        songs   = [tuple((s.Name, s.SongID)) for s in Songs.query.all()]
        albums  = [tuple((al.Title, al.AlbumID)) for al in Albums.query.all()]
        tours   = [tuple((t.Name, t.TourID)) for t in Tours.query.all()]
        genre   = [tuple((g.Name, g.GID)) for g in Genre.query.all()]
        if _type == "artist":
            artists = Artists.query.filter(Artists.ArtistID == _id).first()
            artists.ArtistGenre
            info = artists.__dict__
            song_list = []
            for s in artists.Songs:
                song_list.append(tuple((s.Name, s.SongID)))
            info['SongList'] = song_list
            album_list = []
            for al in artists.Albums:
                album_list.append(tuple((al.Title, al.AlbumID)))
            info['AlbumList'] = album_list
            tour_list = []
            for t in artists.Tours:
                tour_list.append(tuple((t.Name, t.TourID)))
            info['TourList'] = tour_list
            info['ArtistGenre'] = [(a.Name, a.GID) for a in info['ArtistGenre']]
        elif _type == "song":
            songs = Songs.query.filter(Songs.SongID == _id).first()
            songs.SongGenre
            info = songs.__dict__
            info['SongGenre'] = [(a.Name, a.GID) for a in info['SongGenre']]
        elif _type == "album":
            albums = Albums.query.filter(Albums.AlbumID == _id).first()
            info = albums.__dict__
        elif _type == "tour":
            tours = Tours.query.filter(Tours.TourID == _id).first()
            info = tours.__dict__
        print(info)
        return render_template('edit.html', _type = _type, _id = _id, info=info, artists=artists, songs=songs, albums=albums, tours=tours,
                                genre=genre, recaptcha=recaptcha)
    elif request.method == 'POST': # here starts editing or deleting
        if not recaptcha.verify():
            return redirect(url_for("edit", _type=_type, _id=_id, methods="GET"))
        if _type == 'artist':
            artist = Artists.query.filter(Artists.ArtistID == _id).first()
            if request.form.get('delete'):
                db.session.delete(artist)
                db.session.commit()
                return redirect("http://banddb.me")
            else:
                artist.Image = request.form.get('img')
                artist.Start_Time = request.form.get('start-year')
                artist.End_Time = request.form.get('end-year')  # use this to hold form content, delete will a param passed in form
# ---------------------------------
# check deleting relationship later
# ---------------------------------
                artist.ArtistGenre = []
                for gid in request.form.getlist('genres'):
                    artistGenre = Genre.query.filter(Genre.GID == gid).first()
                    artist.ArtistGenre.append(artistGenre)

                db.session.commit()
                return redirect("http://banddb.me/artists/{0}".format(artist.ArtistID))
        elif _type == 'song':
            song = Songs.query.filter(Songs.SongID == _id).first()
            if request.form.get('delete'):
                db.session.delete(song)
                db.session.commit()
                return redirect("http://banddb.me")
            else:
                song.Image = request.form.get('img')
                song.Creation_Date = request.form.get('release-date')
                song.Run_Time = request.form.get('run-time')
                song.Chart_Position = request.form.get('chart-position')
                song.SongGenre = []
                for gid in request.form.getlist('genres'):
                    songgenre = Genre.query.filter(Genre.GID == gid).first()
                    song.SongGenre.append(songgenre)
                print(song.ArtistID)
                if song.ArtistID:
                    artist = Artists.query.filter(Artists.ArtistID == song.ArtistID).first()
                    artist.Songs.remove(song)
                    db.session.commit()
                new_artist = Artists.query.filter(Artists.ArtistID == int(request.form.get('artists'))).first()
                new_artist.Songs.append(song)
                db.session.commit()
                if song.AlbumID:
                    album = Albums.query.filter(Albums.AlbumID == song.AlbumID).first()
                    album.Songs.remove(song)
                    db.session.commit()
                if int(request.form.get('albums')) != 0:
                    new_album = Albums.query.filter(Albums.AlbumID == int(request.form.get('albums'))).first()
                    new_album.Songs.append(song)
                    db.session.commit()
                return redirect("http://banddb.me/songs/{0}".format(song.SongID))
        elif _type == 'album':
            album = Albums.query.filter(Albums.AlbumID == _id).first()
            if request.form.get('delete'):
                db.session.delete(album)
                db.session.commit()
                return redirect("http://banddb.me")
            else:
                print(album.US_Chart_Position)
                album.Image = request.form.get('img')
                album.Year = request.form.get('year')
                album.US_Chart_Position = request.form.get('chart-position')
                print(request.form.get('chart-position'))
                if album.ArtistID:
                    artist = Artists.query.filter(Artists.ArtistID == album.ArtistID).first()
                    artist.Albums.remove(album)
                    db.session.commit()
                if int(request.form.get('artists')) != 0:
                    new_artist = Artists.query.filter(Artists.ArtistID == int(request.form.get('artists'))).first()
                    new_artist.Albums.append(album)
                    db.session.commit()
                print(album.US_Chart_Position)
                return redirect("http://banddb.me/albums/{0}".format(album.AlbumID))
        elif _type == 'tour':
            tour = Tours.query.filter(Tours.TourID == _id).first()
            if request.form.get('delete'):
                db.session.delete(tour)
                db.session.commit()
                return redirect("http://banddb.me")
            else:
                tour.Image = request.form.get('img')
                tour.tDate = getDate(request.form.get('dates'))
                tour.Venue = request.form.get('venue')
                tour.Locations = request.form.get('locations')
                tour.TourLineUp = []
                # for s in request.form.get('songs'):
                #     song = Songs.query.filter(Songs.SongID == s).first()
                #     tour.TourLineUp.append(song)
                if tour.ArtistID:
                    artist = Artists.query.filter(Artists.ArtistID == tour.ArtistID).first()
                    artist.Tours.remove(tour)
                    db.session.commit()
                print(int(request.form.get('artists')))
                if int(request.form.get('artists')) != 0:
                    new_artist = Artists.query.filter(Artists.ArtistID == int(request.form.get('artists'))).first()
                    new_artist.Tours.append(tour)
                    db.session.commit()
                return redirect("http://banddb.me/tours/{0}".format(tour.TourID))
# redirect after finishing editing or deleting

#request POST
#request.form.get('start_date']


@app.route('/add/<string:_type>', methods=['GET', 'POST'], strict_slashes=False)
def add(_type):
    if request.method == 'GET':
        artists = [tuple((a.Name, a.ArtistID)) for a in Artists.query.all()]
        songs   = [tuple((s.Name, s.SongID)) for s in Songs.query.all()]
        albums  = [tuple((al.Title, al.AlbumID)) for al in Albums.query.all()]
        tours   = [tuple((t.Name, t.TourID)) for t in Tours.query.all()]
        genre   = [tuple((g.Name, g.GID)) for g in Genre.query.all()]
        return render_template('add.html', _type=_type, artists=artists, songs=songs, albums=albums, tours=tours,
                                genre=genre, recaptcha=recaptcha)
    elif request.method == 'POST':
        if not recaptcha.verify():
            return redirect(url_for("add", _type=_type, methods="GET"))
        if _type == 'artist':
            NewArtist = Artists(name=request.form.get('name'),
                                image=request.form.get('img'),
                                start_time=request.form.get('start-year'),
                                end_time=request.form.get('end-year'))
#            genre
            for gid in request.form.getlist('genres'):
                artistGenre = Genre.query.filter(Genre.GID == gid).first()
                NewArtist.ArtistGenre.append(artistGenre)
#            album
            for a in request.form.getlist('albums'):
                artistAlbum = Albums.query.filter(Albums.AlbumID == a).first()
                NewArtist.Albums.append(artistAlbum)

#            tour
            for t in request.form.getlist('tours'):
                artistTour = Tours.query.filter(Tours.TourID == t).first()
                NewArtist.Tours.append(artistTour)

            db.session.add(NewArtist)
            db.session.commit()
# -----------------------
# check redirection later
# -----------------------
            return redirect("http://banddb.me/artists/{0}/".format(NewArtist.ArtistID))
        elif _type == 'song':
            print("SONG")
            NewSong = NewSong = Songs(name=request.form.get('name'),
                creation_date = getDate(request.form.get('release-date')),
                run_time = request.form.get('run-time'),
                image = request.form.get('img'),
                chart_position = request.form.get('chart-position'))
            print('Cteated new song')
#           genre
            for gid in request.form.getlist('genres'):
                songGenre = Genre.query.filter(Genre.GID == gid).first()
                NewSong.SongGenre.append(songGenre)
            print('Added genre')
#           artist
            a = request.form.getlist('artists')
            if len(a) != 0 and int(a[0]) != 0:
                artist = Artists.query.filter(Artists.ArtistID == int(a[0]))
                for a in artist:
                    a.Songs.append(NewSong)
#           album
            a = request.form.getlist('albums')
            if len(a) != 0 and int(a[0]) != 0:
                album = Albums.query.filter(Albums.AlbumID == int(a[0]))
                for a in album:
                    a.Songs.append(NewSong)

            db.session.add(NewSong)
            db.session.commit()
            return redirect("http://banddb.me/songs/{0}".format(NewSong.SongID))
        elif _type == 'album':
            NewAlbum = Albums(title=request.form.get('name'),
                year=getDate(request.form.get('dates')),
                image=request.form.get('img'),
                us_chart_position=request.form.get('chart-position'))
#           artist
            a = request.form.getlist('artists')

            if len(a) != 0 and int(a[0]) != 0:
                artist = Artists.query.filter(Artists.ArtistID == int(a[0]))
                for a in artist:
                    a.Albums.append(NewAlbum)
#           song
            for s in request.form.getlist('songs'):
                song = Songs.query.filter(Songs.SongID == s).first()
                NewAlbum.Songs.append(song)

            db.session.add(NewAlbum)
            db.session.commit()
            return redirect("http://banddb.me/albums/{0}".format(NewAlbum.AlbumID))
        elif _type == 'tour':
            NewTour = Tours(date=request.form.get('dates'),
                            name=request.form.get('name'),
                            image=request.form.get('img'),
                            venue=request.form.get('venue'),
                            locations=request.form.get('locations'))
#           artist
            a = request.form.getlist('artists')
            if len(a) != 0 and int(a[0]) != 0:
                artist = Artists.query.filter(Artists.ArtistID == int(a[0]))
                for a in artist:
                    a.Tours.append(NewTour)
#           album
            for s in request.form.getlist('songs'):
                song = Songs.query.filter(Songs.SongID == s).first()
                NewTour.TourLineUp.append(song)

            db.session.add(NewTour)
            db.session.commit()
            return redirect("http://banddb.me/tours/{0}".format(NewTour.TourID))


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def all_other(path):
    print('You want path: %s' % path)
    return render_template('index.html')


@app.route('/')
def index():
    """
    Doc.

    Doc.
    """
    return render_template('index.html')



@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# INFO

rom flask_restless import APIManager

# Create the Flask-Restless API manager.
manager = APIManager(app, flask_sqlalchemy_db=db)

# Create API endpoints, which will be available at /api/<tablename> by
# default. Allowed HTTP methods can be specified as well.
manager.create_api(Artists, methods=['GET'], results_per_page=12)
manager.create_api(Songs, methods=['GET'], results_per_page=12)
manager.create_api(Albums, methods=['GET'], results_per_page=12)
manager.create_api(Genre, methods=['GET'], results_per_page=12)
manager.create_api(Tours, methods=['GET'], results_per_page=12)


@app.teardown_request
def teardown_request(exception):
    if exception:
        db.session.rollback()
        db.session.remove()
    db.session.remove()
