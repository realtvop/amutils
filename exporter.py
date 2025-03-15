import csv
import os  # Make sure os is imported at the file level
import bridge

def export_tracks_to_csv(output_path):
    """
    Export track list to CSV file with id, name, album, artist, album artist, play count, favorite status, duration, and file path.
    
    Args:
        output_path (str): Path to save the CSV file
    
    Returns:
        bool: True if export was successful, False otherwise
    """
    try:
        tracks = bridge.get_all_tracks()
        
        if not tracks:
            print("No tracks found in your library.")
            return False
        
        try:
            # Use 'utf-8-sig' encoding which includes BOM for Excel compatibility
            with open(output_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = ['id', 'name', 'album', 'artist', 'album_artist', 'play_count', 'is_favorite', 'duration', 'file_path']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for track in tracks:
                    writer.writerow({
                        'id': track.id,
                        'name': track.name,
                        'album': track.album,
                        'artist': track.artist,
                        'album_artist': track.album_artist,
                        'play_count': track.play_count,
                        'is_favorite': track.is_favorite,
                        'duration': track.duration,
                        'file_path': track.file_path
                    })
                    
            print(f"Successfully exported {len(tracks)} tracks to {output_path}")
            return True
        except Exception as e:
            print(f"Error writing CSV file: {e}")
            return False
            
    except AttributeError:
        print("Error: The bridge module doesn't support track export functionality.")
        print("Please make sure you have the latest version of this application.")
        return False

def import_tracks_from_csv(input_path):
    """
    Import track information from CSV file and update tracks in Apple Music.
    
    The CSV file can be in one of two formats:
    1. Standard format with 'id' column (from export_tracks_to_csv)
    2. Matched tracks format with 'File Directory' column
    
    Args:
        input_path (str): Path to the CSV file
        
    Returns:
        bool: True if import was successful, False otherwise
    """
    # Import os directly in the function to ensure it's available
    import os
    
    if not os.path.exists(input_path):
        print(f"Error: File does not exist: {input_path}")
        return False
        
    try:
        updated_count = 0
        failed_count = 0
        skipped_count = 0
        duration_matched_count = 0
        
        # Try multiple encodings in case of issues
        encodings = ['utf-8-sig', 'utf-8', 'latin-1', 'gb18030', 'shift_jis']
        
        for encoding in encodings:
            try:
                with open(input_path, 'r', newline='', encoding=encoding) as csvfile:
                    reader = csv.DictReader(csvfile)
                    
                    # Check if this is a standard format or matched tracks format
                    is_standard_format = 'id' in reader.fieldnames
                    is_matched_format = 'File Directory' in reader.fieldnames
                    has_duration = 'Duration(s)' in reader.fieldnames
                    
                    if not (is_standard_format or is_matched_format):
                        print(f"Error: CSV file must contain either 'id' or 'File Directory' column")
                        return False
                    
                    # Store rows so we can process them after determining format
                    rows = list(reader)
                    
                    # Process each row
                    for row in rows:
                        if is_standard_format:
                            track_id = row.get('id')
                            if track_id:
                                # Standard import by ID
                                # Extract all possible fields to update
                                name = row.get('name')
                                album = row.get('album')
                                artist = row.get('artist')
                                play_count = int(row.get('play_count')) if row.get('play_count', '').isdigit() else None
                                is_favorite = row.get('is_favorite')
                                
                                # Convert string representation of boolean to actual boolean
                                if is_favorite is not None:
                                    if is_favorite.lower() in ('true', '1', 'yes', 'y'):
                                        is_favorite = True
                                    elif is_favorite.lower() in ('false', '0', 'no', 'n'):
                                        is_favorite = False
                                    else:
                                        is_favorite = None
                                
                                # Update track information including name, album, and artist
                                if bridge.update_track_by_id(track_id, play_count, is_favorite, name, album, artist):
                                    updated_count += 1
                                else:
                                    failed_count += 1
                        
                        elif is_matched_format:
                            # Matched tracks import by file path
                            file_path = row.get('File Directory')
                            title = row.get('Title')
                            album = row.get('Album')
                            artist = row.get('Artist')
                            album_artist = row.get('Album Artist')
                            duration = row.get('Duration(s)')
                            
                            if file_path:
                                # Try to find track by file path
                                track = bridge.get_track_by_file_path(file_path)
                                
                                if track:
                                    # Update the track with matched information
                                    if bridge.update_track_info(track, title, album, artist, album_artist):
                                        updated_count += 1
                                    else:
                                        failed_count += 1
                                else:
                                    # Second attempt: try with just the filename if full path failed
                                    filename = os.path.basename(file_path.rstrip('/'))
                                    if filename:
                                        track = bridge.get_track_by_file_path(filename)
                                        
                                        if track:
                                            # Update the track with matched information
                                            if bridge.update_track_info(track, title, album, artist, album_artist):
                                                updated_count += 1
                                                print(f"Successfully matched by filename: {filename}")
                                            else:
                                                failed_count += 1
                                        # Third attempt: try with duration matching if duration is provided
                                        elif has_duration and duration and title:
                                            try:
                                                duration_float = float(duration)
                                                # 移除了标题和艺术家参数，仅使用持续时间匹配
                                                track = bridge.get_track_by_duration(duration_float)
                                                
                                                if track:
                                                    # Update the track with matched information
                                                    if bridge.update_track_info(track, title, album, artist, album_artist):
                                                        duration_matched_count += 1
                                                        print(f"Successfully matched by duration: {title} ({duration}s)")
                                                    else:
                                                        failed_count += 1
                                                else:
                                                    print(f"Could not find track with path or duration: {file_path} ({duration}s)")
                                                    failed_count += 1
                                            except (ValueError, TypeError):
                                                print(f"Invalid duration value: {duration}")
                                                failed_count += 1
                                        else:
                                            print(f"Could not find track with path: {file_path}")
                                            failed_count += 1
                                    else:
                                        print(f"Could not find track with path: {file_path}")
                                        failed_count += 1
                            else:
                                skipped_count += 1
                
                break  # Break out of encoding loop if successful
            except UnicodeDecodeError:
                if encoding == encodings[-1]:
                    print(f"Error: Could not decode the CSV file. Please ensure it's properly encoded.")
                    return False
                continue
        
        print(f"Import complete: {updated_count} tracks updated by path, {duration_matched_count} matched by duration, {failed_count} failed, {skipped_count} skipped")
        return True
    except Exception as e:
        print(f"Error importing CSV: {e}")
        return False

def handle_export_command(path):
    """
    Handle the export command from the CLI.
    
    Args:
        path (str): Path where to save the CSV file
    """
    if path.endswith('.csv'):
        export_tracks_to_csv(path)
    else:
        export_tracks_to_csv(os.path.join(path, 'tracks_export.csv'))

def handle_import_command(path):
    """
    Handle the import command from the CLI.
    
    Args:
        path (str): Path to the CSV file
    """
    if os.path.isdir(path):
        print("Error: Please specify a CSV file, not a directory")
        return
        
    if not path.endswith('.csv'):
        print("Error: File must have .csv extension")
        return
        
    import_tracks_from_csv(path)
