import sys, os, bridge, file_reader, math
import exporter

def print_help():
    print('''amutils - Apple Music Utilities

Usage:

    amutils <command> [file]

Commands:

    stat           get your statistics
    playedtime     get library total played time
    replace        use the given music file(s) to replace the song with the same metadata
    export         export track list to CSV file with id, name, album, artist, play count, and favorite status
    import         import track information from CSV file, matching by track ID
    addtoplaylist  add all tracks with .movpkg in their file path to a specified playlist (usage: addtoplaylist [playlist_name])
''')
    sys.exit(0)

def process_folder(folder_path, folder=True):
    if not os.path.exists(folder_path):
        print(f"Error: Folder or file does not exist")
        return
    songs = file_reader.get_songs_in_folder(os.path.abspath(folder_path)) if folder else [ file_reader.process_file(os.path.abspath(folder_path)) ]
    for song in songs:
        track = bridge.get_song_info(song.meta.title, song.meta.artist, song.meta.album)
        bridge.replace_song(song, track)

def get_played_time():
    days, hours, minutes, seconds, original_minutes = bridge.get_formatted_total_playtime()
    print(f"{math.floor(days)} days, {math.floor(hours)} hrs, {math.floor(minutes)} mins, {math.floor(seconds)} seconds ({math.floor(original_minutes)} minutes)")

def get_stat():
    total_play_time, track_count = bridge.get_total_playtime()
    days, hours, minutes, seconds, original_minutes = bridge.format_time_in_days(total_play_time)
    print(f"You have {track_count} songs in your library")
    print(f"You've listened for {math.floor(days)} days, {math.floor(hours)} hrs, {math.floor(minutes)} mins, {math.floor(seconds)} seconds ({math.floor(original_minutes)} minutes)")

def add_to_playlist(playlist_name):
    """Add all tracks with .movpkg in their file path to a specified playlist."""
    
    # Get all tracks from library
    tracks = bridge.get_all_tracks()
    
    # Filter for tracks that have .movpkg in their file path
    movpkg_tracks = [track for track in tracks if track.file_path and ".movpkg" in track.file_path]
    
    if not movpkg_tracks:
        print("No tracks with .movpkg in their file path found in the library")
        return
    
    # Add tracks to playlist
    count = bridge.add_tracks_to_playlist(movpkg_tracks, playlist_name)
    print(f"Added {count} tracks to playlist '{playlist_name}'")

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help']: print_help()
    
    command = sys.argv[1]
    
    if command == "addtoplaylist":
        if len(sys.argv) < 3:
            print("Error: Missing playlist name. Usage: amutils addtoplaylist [playlist_name]")
            sys.exit(1)
        playlist_name = sys.argv[2]
        add_to_playlist(playlist_name)
    elif command == "replace":
        path = sys.argv[2] if len(sys.argv) >= 3 else os.getcwd()
        process_folder(path, folder=os.path.isdir(path))
    elif command == "playedtime": 
        get_played_time()
    elif command == "stat": 
        get_stat()
    elif command == "export": 
        path = sys.argv[2] if len(sys.argv) >= 3 else os.getcwd()
        exporter.handle_export_command(path)
    elif command == "import": 
        path = sys.argv[2] if len(sys.argv) >= 3 else os.getcwd()
        exporter.handle_import_command(path)
    else:
        print(f"Error: Unknown command '{command}'. Use --help to see available commands.")
        sys.exit(1)

if __name__ == "__main__":
    main()