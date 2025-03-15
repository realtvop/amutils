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
        import re
        
        # Print out all bytes in file_path to debug hidden characters
        print(f"Debug original path: {file_path}")
        hex_bytes = ' '.join([f'{ord(c):x}' for c in file_path])
        print(f"Path bytes (hex): {hex_bytes[:50]}... (truncated)")
        
        # Create clean normalized version of the path
        def deep_clean_path(path):
            if not path:
                return ""
            # Remove any control characters and zero-width spaces
            path = re.sub(r'[\u200B-\u200F\u2028-\u202F\uFEFF]', '', path)
            # Normalize unicode form
            path = unicodedata.normalize('NFC', path)
            # Strip all trailing whitespace, slashes and numbers before extension
            path = re.sub(r'\s+\d+(\.\w+)$', r'\1', path)
            path = path.rstrip('/ ')
            return path
            
        # Create search keys from a path
        def get_path_keys(path):
            """Extract various identifying keys from a path for fuzzy matching"""
            if not path:
                return {}
                
            # Basic path normalization
            clean_path = deep_clean_path(path)
            
            # Get filename components
            filename = os.path.basename(clean_path)
            dirname = os.path.dirname(clean_path)
            
            # Handle .movpkg special case
            is_movpkg = clean_path.endswith('.movpkg')
            if is_movpkg:
                basename = filename[:-7]  # Remove .movpkg
            else:
                basename = os.path.splitext(filename)[0]
                
            # Clean the basename further (remove special chars and numbers)
            simple_basename = re.sub(r'[^\w\s]', '', basename)
            simple_basename = re.sub(r'\s+\d+$', '', simple_basename).strip().lower()
            
            # Get path segments for partial matching
            path_parts = clean_path.split('/')
            # Last 1-3 path segments are most useful for matching
            segments = [p for p in path_parts[-3:] if p]
            
            # For Japanese/special char filenames, create an ASCII-only version
            ascii_name = ''.join(c for c in simple_basename if ord(c) < 128)
            
            return {
                'clean_path': clean_path,
                'filename': filename,
                'basename': basename,
                'simple_basename': simple_basename,
                'dirname': dirname,
                'is_movpkg': is_movpkg,
                'segments': segments,
                'ascii_name': ascii_name
            }
        
        # Get search keys from our target path
        target_keys = get_path_keys(file_path)
        print(f"Matching basename: '{target_keys['basename']}'")
        
        # Special log helper
        def log_match(quality, track, reason):
            try:
                track_name = track.name()
                artist_name = track.artist()
                track_path = str(track.location())
                filename = os.path.basename(track_path)
                print(f"Match ({quality}): '{track_name}' by '{artist_name}' - {reason}")
                print(f"Path: {filename}")
            except:
                print(f"Match ({quality}): [details unavailable] - {reason}")
        
        # First try direct lookup for better performance
        if target_keys['is_movpkg']:
            try:
                # Try to find directly by name if it's a .movpkg (usually more reliable than path)
                dir_name = os.path.basename(os.path.dirname(file_path))
                name_to_search = target_keys['basename']
                
                # Clean up the name for better matching
                name_to_search = re.sub(r'\s+\d+$', '', name_to_search)
                name_to_search = re.sub(r'(?: \(feat\..+?\)|­+)$', '', name_to_search)
                
                print(f"Trying direct lookup by name: '{name_to_search}'")
                exact_match_tracks = library.tracks[its.name == name_to_search]
                if exact_match_tracks.count() > 0:
                    track = exact_match_tracks.first()
                    log_match('DIRECT', track, "exact name match")
                    return track
            except Exception as e:
                print(f"Direct lookup error: {e}")
        
        # Collect matches with their quality scores
        matches = []
        
        # Try each track with various matching strategies
        for track in tracks:
            try:
                # Skip tracks without location
                location = track.location()
                if location is None:
                    continue
                
                # Get the track's path and extract search keys
                track_path = str(location)
                track_keys = get_path_keys(track_path)
                
                # Direct match - highest priority 
                if target_keys['clean_path'] == track_keys['clean_path']:
                    matches.append((100, track, "exact path match"))
                    continue
                
                # Exact filename match (very reliable)
                if target_keys['filename'] == track_keys['filename']:
                    matches.append((90, track, "exact filename match"))
                    continue
                
                # Base filename match (without extension or numbers)
                if target_keys['basename'] == track_keys['basename']:
                    matches.append((80, track, "basename match"))
                    continue
                
                # Simple basename match (ignoring special chars and numbers)
                if target_keys['simple_basename'] and target_keys['simple_basename'] == track_keys['simple_basename']:
                    matches.append((70, track, "simple basename match"))
                    continue
                    
                # For .movpkg files specifically
                if target_keys['is_movpkg'] and track_keys['is_movpkg']:
                    # Special case: try without version numbers at the end (e.g. "song 2.movpkg")
                    if re.sub(r'\s+\d+$', '', target_keys['basename']) == re.sub(r'\s+\d+$', '', track_keys['basename']):
                        matches.append((65, track, ".movpkg basename match without numbers"))
                        continue
                
                # Check if track filename contains our target basename
                if target_keys['basename'] in track_keys['filename']:
                    matches.append((60, track, "filename contains target basename"))
                    continue
                    
                # Last segments matching (useful for nested paths)
                common_segments = set(target_keys['segments']).intersection(set(track_keys['segments']))
                if len(common_segments) >= 2:
                    matches.append((50, track, f"{len(common_segments)} common path segments"))
                    continue
                
                # Parent directory matches + similar filename 
                if (os.path.basename(target_keys['dirname']) == os.path.basename(track_keys['dirname']) and
                    len(target_keys['simple_basename']) > 3 and 
                    target_keys['simple_basename'] in track_keys['simple_basename']):
                    matches.append((40, track, "same directory, similar filename"))
                    continue
                
                # For ASCII-only simplified matching (when nothing else works)
                if (len(target_keys['ascii_name']) > 3 and target_keys['ascii_name'] == track_keys['ascii_name']):
                    matches.append((30, track, "ASCII-only name match"))
                    continue
                    
            except Exception as e:
                # Skip tracks with errors
                continue
                
        # Sort by match quality and return best match
        if matches:
            matches.sort(key=lambda x: x[0], reverse=True)
            best_match = matches[0][1]
            log_match(matches[0][0], best_match, matches[0][2])
            return best_match
            
        # If we get here, we've tried everything and found nothing
        print(f"No matching track found in library for: {file_path}")
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
            
        print(f"Searching for track with duration: {duration}s (tolerance: {tolerance}s)")
        
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
                    matching_tracks.append((track, abs(track_duration - float(duration))))
            except Exception:
                continue
                
        if matching_tracks:
            # Sort by duration difference
            matching_tracks.sort(key=lambda x: x[1])
            
            # Print some debug info for top matches
            for i, (track, diff) in enumerate(matching_tracks[:3]):
                try:
                    print(f"Match {i+1}: '{track.name()}' by '{track.artist()}' - {track.duration()}s (diff: {diff:.3f}s)")
                except:
                    print(f"Match {i+1}: [track name unavailable] - {track.duration()}s (diff: {diff:.3f}s)")
            
            # Return the closest duration match
            return matching_tracks[0][0]
            
        # No match found
        print(f"No tracks found with duration close to {duration}s (tolerance: {tolerance}s)")
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

def get_track_by_title_and_artist(title, artist=None):
    """
    Find a track in the Apple Music library by its title and artist.
    
    Args:
        title (str): The title of the track
        artist (str, optional): The artist name
        
    Returns:
        An appscript track object if found, None otherwise
    """
    try:
        if not title:
            return None
            
        # Create search condition
        condition = its.name.contains(title)
        if artist:
            condition = condition.AND(its.artist.contains(artist))
            
        # Find track
        library = app.library_playlists[1]
        tracks = library.tracks[condition]
        
        # Return first match if any
        if tracks.count():
            return tracks.first()
        return None
        
    except Exception as e:
        print(f"Error finding track by title/artist: {e}")
        return None

def get_track_by_title_artist_combo(title, artist=None, album=None):
    """
    Find a track by its title and artist combination. More flexible than the path matching.
    
    Args:
        title (str): The title of the track 
        artist (str, optional): The artist name
        album (str, optional): The album name
        
    Returns:
        An appscript track object if found, None otherwise
    """
    try:
        if not title:
            return None
        
        print(f"Searching for track: '{title}' by '{artist or 'any artist'}'")
        
        # Get library tracks
        library = app.library_playlists[1]
        
        # First try exact match
        if artist and album:
            tracks = library.tracks[its.name == title and its.artist == artist and its.album == album]
            if tracks.count() > 0:
                return tracks.first()
        
        if artist:
            tracks = library.tracks[its.name == title and its.artist == artist]
            if tracks.count() > 0:
                return tracks.first()
        
        # Then try contains match
        if artist:
            tracks = library.tracks[its.name.contains(title) and its.artist.contains(artist)]
            if tracks.count() > 0:
                return tracks.first()
        
        # Last resort, just title match
        tracks = library.tracks[its.name.contains(title)]
        if tracks.count() > 0:
            return tracks.first()
        
        return None
    except Exception as e:
        print(f"Error finding track by title/artist: {e}")
        return None

def add_files_to_playlist(file_paths, playlist_name):
    """
    Add files to a specified Apple Music playlist.
    
    Args:
        file_paths: List of paths to .movpkg files to add
        playlist_name: Name of the playlist to add files to
    
    Returns:
        Number of files successfully added
    """
    import appscript
    
    itunes = appscript.app('Music')
    
    # Try to find the playlist, create it if it doesn't exist
    try:
        playlist = itunes.playlists[playlist_name].get()
    except:
        playlist = itunes.make(new=appscript.k.playlist, with_properties={'name': playlist_name})
    
    added_count = 0
    
    for file_path in file_paths:
        try:
            # Add the file to iTunes library and the playlist
            track = itunes.add(file_path, to=playlist)
            added_count += 1
        except Exception as e:
            print(f"Failed to add {file_path}: {str(e)}")
    
    return added_count

def add_tracks_to_playlist(tracks, playlist_name):
    """
    Add existing library tracks to a specified Apple Music playlist.
    
    Args:
        tracks: List of track objects from get_all_tracks()
        playlist_name: Name of the playlist to add tracks to
    
    Returns:
        Number of tracks successfully added
    """
    try:
        # Try to find the playlist, create it if it doesn't exist
        try:
            playlist = app.playlists[playlist_name].get()
        except:
            playlist = app.make(new=app.k.playlist, with_properties={'name': playlist_name})
        
        added_count = 0
        
        for track in tracks:
            try:
                # Find the actual track object using the ID
                library_track = app.library_playlists[1].tracks[its.id == int(track.id)].first()
                
                # Duplicate the track to the playlist
                library_track.duplicate(to=playlist)
                added_count += 1
                print(f"Added '{track.name}' by {track.artist} to playlist '{playlist_name}'")
            except Exception as e:
                print(f"Failed to add track '{track.name}': {str(e)}")
        
        return added_count
    except Exception as e:
        print(f"Error creating or accessing playlist: {str(e)}")
        return 0