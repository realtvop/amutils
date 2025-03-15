import csv
import os
import bridge

def export_tracks_to_csv(output_path):
    """
    Export track list to CSV file with id, name, album, artist, play count, and favorite status.
    
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
                fieldnames = ['id', 'name', 'album', 'artist', 'play_count', 'is_favorite']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for track in tracks:
                    writer.writerow({
                        'id': track.id,
                        'name': track.name,
                        'album': track.album,
                        'artist': track.artist,
                        'play_count': track.play_count,
                        'is_favorite': track.is_favorite
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
