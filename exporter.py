import csv
import os
import bridge

def export_tracks_to_csv(output_path):
    """
    Export track list to CSV file with id, name, album, artist, play count, favorite status, and SHA256 hash.
    
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
                fieldnames = ['id', 'name', 'album', 'artist', 'play_count', 'is_favorite', 'sha256']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for track in tracks:
                    writer.writerow({
                        'id': track.id,
                        'name': track.name,
                        'album': track.album,
                        'artist': track.artist,
                        'play_count': track.play_count,
                        'is_favorite': track.is_favorite,
                        'sha256': track.sha256
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
    
    Args:
        input_path (str): Path to the CSV file
        
    Returns:
        bool: True if import was successful, False otherwise
    """
    if not os.path.exists(input_path):
        print(f"Error: File does not exist: {input_path}")
        return False
        
    try:
        updated_count = 0
        failed_count = 0
        
        # Try multiple encodings in case of issues
        encodings = ['utf-8-sig', 'utf-8', 'latin-1']
        
        for encoding in encodings:
            try:
                with open(input_path, 'r', newline='', encoding=encoding) as csvfile:
                    reader = csv.DictReader(csvfile)
                    
                    # Verify required fields
                    required_fields = ['id']
                    if not all(field in reader.fieldnames for field in required_fields):
                        print(f"Error: CSV file must contain the field 'id'")
                        return False
                    
                    # Process each row
                    for row in reader:
                        track_id = row.get('id')
                        if not track_id:
                            continue
                            
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
                
                break
            except UnicodeDecodeError:
                if encoding == encodings[-1]:
                    print(f"Error: Could not decode the CSV file. Please ensure it's properly encoded.")
                    return False
                continue
        
        print(f"Import complete: {updated_count} tracks updated, {failed_count} failed")
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
