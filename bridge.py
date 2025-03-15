from appscript import app as attach, its
from types import SimpleNamespace
import hashlib

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

def calculate_file_sha256(file_path):
    """
    Calculate SHA256 hash of a file.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: SHA256 hash as hexadecimal string, or empty string if error
    """
    try:
        if not file_path:
            return ""
            
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            # Read and update hash in chunks to efficiently handle large files
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        print(f"Error calculating hash for {file_path}: {e}")
        return ""

def get_all_tracks():
    """
    Get all tracks from the Apple Music library with their id, name, album, artist, album artist, play count, favorite status, duration, and file path.
    
    Returns:
        list: A list of track objects with id, name, album, artist, album_artist, play_count, is_favorite, duration, and file_path attributes
    """
    from collections import namedtuple
    
    # Create a track object to store information
    Track = namedtuple('Track', ['id', 'name', 'album', 'artist', 'album_artist', 'play_count', 'is_favorite', 'duration', 'file_path'])
    
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
                
                # Get album artist (might be different from the track artist)
                try:
                    album_artist_name = track.album_artist()
                except:
                    album_artist_name = artist_name  # Default to regular artist if album artist is not available
                
                play_count = track.played_count()
                is_favorite = track.favorited()
                
                # Get track duration in seconds and round to one decimal place
                duration = round(track.duration(), 1)
                
                # Get file path (if available)
                try:
                    file_path = track.location().path
                except:
                    file_path = ""
                
                result.append(Track(
                    id=str(track_id),
                    name=track_name,
                    album=album_name,
                    artist=artist_name,
                    album_artist=album_artist_name,
                    play_count=play_count,
                    is_favorite=bool(is_favorite),
                    duration=duration,
                    file_path=file_path
                ))
            except Exception as e:
                print(f"Error processing track: {e}")
                continue
                
        return result
    except Exception as e:
        print(f"Failed to get tracks: {e}")
        return []

def update_track_by_id(track_id, play_count=None, is_favorite=None, name=None, album=None, artist=None):
    """
    Update track information based on track ID.
    
    Args:
        track_id (str): ID of the track to update
        play_count (int, optional): New play count value
        is_favorite (bool, optional): New favorite status
        name (str, optional): New track name
        album (str, optional): New album name
        artist (str, optional): New artist name
        
    Returns:
        bool: True if track was found and updated, False otherwise
    """
    try:
        # Find the track by ID
        track = app.library_playlists[1].tracks[its.id == int(track_id)].first()
        
        # Update play count if provided
        if play_count is not None:
            track.played_count.set(play_count)
            
        # Update favorite status if provided
        if is_favorite is not None:
            track.favorited.set(is_favorite)
            
        # Update track name if provided
        if name is not None and name.strip():
            track.name.set(name)
            
        # Update album name if provided
        if album is not None and album.strip():
            track.album.set(album)
            
        # Update artist name if provided
        if artist is not None and artist.strip():
            track.artist.set(artist)
            
        return True
    except Exception as e:
        print(f"Error updating track {track_id}: {e}")
        return False

def get_track_by_file_path(file_path):
    """
    Find a track in the Apple Music library by its file path.
    
    Args:
        file_path (str): The file path to search for
        
    Returns:
        An appscript track object if found, None otherwise
    """
    try:
        if not file_path:
            return None
            
        # Get all tracks from the library
        library = app.library_playlists[1]
        tracks = library.tracks()
        
        # Get the filename for fallback matching
        import os
        import unicodedata
        
        # Normalize the input path for better matching
        def normalize_path(path):
            if not path:
                return ""
            # Convert to NFC form (preferred for macOS)
            path = unicodedata.normalize('NFC', path)
            # Strip trailing slashes
            path = path.rstrip('/')
            return path
            
        # Prepare the original path and variations for matching
        normalized_path = normalize_path(file_path)
        
        # Get base filename for fallback matching (both with and without extension)
        filename = os.path.basename(normalized_path)
        filename_no_ext = os.path.splitext(filename)[0]
        
        # Prepare matching strategies
        path_components = normalized_path.split('/')
        # Get the last 3 components if available (most likely to be unique)
        last_components = '/'.join(path_components[-3:]) if len(path_components) >= 3 else normalized_path
        
        # Additional fallbacks for movpkg directories
        if normalized_path.endswith('.movpkg'):
            # Also try without .movpkg
            non_movpkg_path = normalized_path[:-7]
            filename_non_movpkg = os.path.basename(non_movpkg_path)
        else:
            non_movpkg_path = None
            filename_non_movpkg = None
            
        # Check each track to see if its location matches any of our paths
        for track in tracks:
            try:
                # Try to get the track location
                location = track.location()
                if location is None:
                    continue
                    
                track_path = str(location)
                normalized_track_path = normalize_path(track_path)
                
                # Match strategy 1: Exact path match
                if normalized_path == normalized_track_path:
                    return track
                    
                # Match strategy 2: Path contains our path (for partial matches)
                if normalized_path in normalized_track_path or normalized_track_path in normalized_path:
                    return track
                    
                # Match strategy 3: Last components matching
                if last_components in normalized_track_path:
                    return track
                    
                # Match strategy 4: Filename matching
                track_filename = os.path.basename(normalized_track_path)
                if filename and (filename == track_filename):
                    return track
                    
                # Match strategy 5: Filename without extension
                track_filename_no_ext = os.path.splitext(track_filename)[0]
                if filename_no_ext and (filename_no_ext == track_filename_no_ext):
                    return track
                    
                # Match strategy 6: Check for .movpkg variations
                if non_movpkg_path and (non_movpkg_path in normalized_track_path or 
                   filename_non_movpkg == track_filename_no_ext):
                    return track
                    
                # Match strategy 7: Check if the filename is a substring of track path
                # This helps when special characters are causing comparison issues
                if filename and filename in normalized_track_path:
                    return track
                    
                # Match strategy 8: Handle numeric IDs in filenames (like 26791805)
                if filename_no_ext.isdigit() and track_filename_no_ext.isdigit():
                    if filename_no_ext == track_filename_no_ext:
                        return track
                    
            except Exception:
                # Skip tracks that have issues with location
                continue
                
        # No match found
        return None
    except Exception as e:
        print(f"Error finding track by file path: {e}")
        return None

def get_track_by_duration(duration, tolerance=0.1):
    """
    Find a track in the Apple Music library by its duration with precise matching.
    
    Args:
        duration (float): The duration of the track in seconds
        tolerance (float, optional): Allowed duration difference in seconds (default: 0.1)
        
    Returns:
        An appscript track object if found, None otherwise
    """
    try:
        if not duration:
            return None
            
        # Get all tracks from the library
        library = app.library_playlists[1]
        tracks = library.tracks()
        
        # Find all tracks with matching duration within tolerance
        matching_tracks = []
        for track in tracks:
            try:
                track_duration = track.duration()
                
                # Check if duration is within tolerance
                if abs(track_duration - float(duration)) <= tolerance:
                    matching_tracks.append(track)
            except Exception:
                continue
                
        if matching_tracks:
            # Return the closest duration match
            return min(matching_tracks, key=lambda t: abs(t.duration() - float(duration)))
            
        # No match found
        return None
    except Exception as e:
        print(f"Error finding track by duration: {e}")
        return None

def update_track_info(track, name=None, album=None, artist=None, album_artist=None, play_count=None, is_favorite=None):
    """
    Update various information for a track.
    
    Args:
        track: The appscript track object to update
        name (str, optional): New track name
        album (str, optional): New album name
        artist (str, optional): New artist name
        album_artist (str, optional): New album artist
        play_count (int, optional): New play count
        is_favorite (bool, optional): New favorite status
        
    Returns:
        bool: True if updated successfully, False otherwise
    """
    try:
        # Update track name if provided
        if name is not None and name.strip():
            track.name.set(name)
            
        # Update album name if provided
        if album is not None and album.strip():
            track.album.set(album)
            
        # Update artist name if provided
        if artist is not None and artist.strip():
            track.artist.set(artist)
            
        # Update album artist if provided
        if album_artist is not None and album_artist.strip():
            track.album_artist.set(album_artist)
            
        # Update play count if provided
        if play_count is not None:
            track.played_count.set(play_count)
            
        # Update favorite status if provided
        if is_favorite is not None:
            track.favorited.set(is_favorite)
            
        return True
    except Exception as e:
        print(f"Error updating track information: {e}")
        return False