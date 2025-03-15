from appscript import app as attach, its
from types import SimpleNamespace

app = attach('Music')

playlists = app.playlists()

def get_song_info(track_name, artist, album):
    try:
        conditions = its.name == track_name
        if artist: conditions = conditions and its.artist == artist
        if album: conditions = conditions and its.album == album
        track = app.library_playlists[1].tracks[conditions].first()
        
        id = track.id()
        play_count = track.played_count()
        date_added = track.date_added()
        favorite = track.favorited()
        location = track.location().path

        containing_playlists = []

        for playlist in playlists:
            if playlist.tracks[its.persistent_ID == track.persistent_ID()].exists():
                containing_playlists.append(playlist)

        return SimpleNamespace(
            track=track,
            id=id,
            play_count=play_count,
            date_added=date_added,
            favorite=favorite,
            location=location,
            containing_playlists=containing_playlists,
        )

    except Exception as e:
        print(f"Error finding track: {e}")

def replace_song(file, track):
    try:
        if track: track.track.delete()
        newer = app.add(file.path)
        if track:
            # if newer.location().path == track.location: return
            newer.played_count.set(track.play_count)
            newer.favorited.set(track.favorite)
            for playlist in track.containing_playlists:
                newer.duplicate(to=playlist.end())
    except Exception as e:
        print(f"Error replacing song: {e}")

def get_total_playtime():
    try:
        library = app.library_playlists[1]
        tracks = library.tracks()
        total_duration = 0
        for track in tracks:
            duration = track.duration()
            play_count = track.played_count()
            total_duration += duration * play_count
        return total_duration, len(tracks)
    except Exception as e:
        print(f"Error: {e}")
        return 0

def format_time_in_days(seconds):
    original_minutes = seconds // 60
    days = seconds // (24 * 3600)
    seconds %= (24 * 3600)
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return days, hours, minutes, seconds, original_minutes

def get_formatted_total_playtime():
    return format_time_in_days(get_total_playtime()[0])

def get_all_tracks():
    """
    Get all tracks from the Apple Music library with their id, name, play count, and favorite status.
    
    Returns:
        list: A list of track objects with id, name, album, artist, play_count, and is_favorite attributes
    """
    from collections import namedtuple
    
    # Create a track object to store information
    Track = namedtuple('Track', ['id', 'name', 'album', 'artist', 'play_count', 'is_favorite'])
    
    try:
        # Use appscript to query Apple Music library (consistent with other functions)
        library = app.library_playlists[1]
        tracks = library.tracks()
        
        result = []
        for track in tracks:
            try:
                # Get track information
                track_id = track.id()
                track_name = track.name()
                album_name = track.album()
                artist_name = track.artist()
                play_count = track.played_count()
                is_favorite = track.favorited()
                
                result.append(Track(
                    id=str(track_id),
                    name=track_name,
                    album=album_name,
                    artist=artist_name,
                    play_count=play_count,
                    is_favorite=bool(is_favorite)
                ))
            except Exception as e:
                print(f"Error processing track: {e}")
                continue
                
        return result
    except Exception as e:
        print(f"Failed to get tracks: {e}")
        return []