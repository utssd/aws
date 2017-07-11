"""
A Json Parser for insertions
"""

from dbModels import *

# connect database

# read json file

# parsing

# insertions

# close databases


# ***********
# playground
# ***********

import json
from pprint import pprint

with open('data.json') as data_file:
    data = json.load(data_file)

db.drop_all()
db.create_all()


def getDate(s, f="%d %b %Y, %H:%M"):
    return datetime.datetime.strptime(s, f).date().isoformat()


def getRunTime(s):
    return int(s) // 1000


for album, albumContent in data['albums'].items():
    NewAlbum = Albums(title=albumContent['name'], year=getDate(
        albumContent['release_date']), image=albumContent['img'], us_chart_position=albumContent['chart_pos'])
    db.session.add(NewAlbum)
    db.session.commit()


for song, songContent in data['songs'].items():
    NewSong = Songs(name=songContent['name'], creation_date=getDate(songContent['release_date']),
                    run_time=getRunTime(songContent['run_time']), image=songContent['img'], chart_position=songContent['chart_pos'])

    gr = songContent['genre']
    if Genre.query.filter(Genre.Name == gr).count():
        NewSong.SongGenre.append(Genre.query.filter(Genre.Name == gr).first())
    else:
        NewGenre = Genre(name=gr)
        NewSong.SongGenre.append(NewGenre)

    # for bugs
    if not songContent['album']['id'] in data['albums']:
        print('ah')
        continue
    albumInfo = data['albums'][songContent['album']['id']]
    if Albums.query.filter(Albums.Title == albumInfo['name'] and Albums.Image == albumInfo['img']).count():
        album = Albums.query.filter(
            Albums.Title == albumInfo['name'] and Albums.Image == albumInfo['img']).first()
        album.Songs.append(NewSong)
    else:
        NewAlbum = Albums(title=albumInfo['name'], year=getDate(
            albumInfo['release_date']), image=albumInfo['img'], us_chart_position=albumInfo['chart_pos'])
        NewAlbum.Songs.append(NewSong)

    artistInfo = data['artists'][songContent['artist']['id']]
    if Artists.query.filter(Artists.Name == artistInfo['name'] and Artists.Image == artistInfo['img']).count():
        artist = Artists.query.filter(
            Artists.Name == artistInfo['name'] and Artists.Image == artistInfo['img']).first()
        artist.Songs.append(NewSong)
    else:
        NewArtist = Artists(name=artistInfo['name'], image=artistInfo['img'], start_time=artistInfo['active']['start'], end_time=artistInfo['active']['end'])
        NewArtist.Songs.append(NewSong)
    db.session.add(NewSong)
    db.session.commit()
    print('ok')


for artist, content in data['artists'].items():
    if Artists.query.filter(Artists.Name == content['name'] and Artists.Image == content['img']).count():
        NewArtist = Artists.query.filter(
            Artists.Name == content['name'] and Artists.Image == content['img']).first()
    else:
        NewArtist = Artists(name=content['name'], image=content['img'], start_time=content['active']['start'], end_time=content['active']['end'])
    # genre info
    for gr in content['genre']:
        if Genre.query.filter(Genre.Name == gr).count():
            NewArtist.ArtistGenre.append(
                Genre.query.filter(Genre.Name == gr).first())
        else:
            NewGenre = Genre(name=gr)
            NewArtist.ArtistGenre.append(NewGenre)

    # album info
    for a in content['albums']:
        # for bugs
        if not a['id'] in data['albums']:
            continue

        albumInfo = data['albums'][a['id']]
        if Albums.query.filter(Albums.Title == albumInfo['name'] and Albums.Image == albumInfo['img']).count():
            NewArtist.Albums.append(Albums.query.filter(
                Albums.Title == albumInfo['name'] and Albums.Image == albumInfo['img']).first())
        else:
            NewAlbum = Albums(title=albumInfo['name'], year=getDate(
                albumInfo['release_date']), image=albumInfo['img'], us_chart_position=albumInfo['chart_pos'])
            NewArtist.Albums.append(NewAlbum)

    # top song info

    for s in content['songs']:
        if not s['id'] in data['songs']:
            continue

        songInfo = data['songs'][s['id']]
        if Songs.query.filter(Songs.Name == songInfo['name'] and Songs.Image == songInfo['img']).count():
            NewArtist.TopSongs.append(Songs.query.filter(
                Songs.Name == songInfo['name'] and Songs.Image == songInfo['img']).first())
        else:
            NewSong = Songs(name=songInfo['name'], creation_date=getDate(
                songInfo['release_date']), run_time=getRunTime(songInfo['run_time']), image=songInfo['img'], chart_position=songInfo['chart_pos'])

            gr = songInfo['genre']
            if Genre.query.filter(Genre.Name == gr).count():
                NewSong.SongGenre.append(
                    Genre.query.filter(Genre.Name == gr).first())
            else:
                NewGenre = Genre(name=gr)
                NewSong.SongGenre.append(NewGenre)

            NewArtist.TopSongs.append(NewSong)

    db.session.add(NewArtist)
    db.session.commit()

print("now tours")
for tour, tourInfo in data['tours'].items():
    NewTour = Tours(date=tourInfo['dates'], name=tourInfo['name'], image=tourInfo['img'], venue=tourInfo['venue'], locations=tourInfo['locations'])
    artist = data['artists'][tourInfo['artist']['id']]
    Artist = Artists.query.filter(Artists.Name == artist['name'] and Artists.Image == artist['img']).first()
    Artist.Tours.append(NewTour)
    for _sc in tourInfo['songs']:
        song = data['songs'][_sc['id']]
        Song = Songs.query.filter(Songs.Name == song['name'] and Songs.Image == song['img']).first()
        print(Song)
        NewTour.TourLineUp.append(Song)
    db.session.add(NewTour)
    db.session.commit()
