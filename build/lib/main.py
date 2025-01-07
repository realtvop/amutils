import sys, os, bridge, file_reader, math

def print_help():
    print('''amutils - Apple Music Utilities

Usage:

    amutils <command> [arguments]

Commands:

    stat           get your statistics
    playedtime     get library total played time
    replace        use the given music file(s) to replace the song with the same metadata
''')
    sys.exit(0)

def process_folder(folder_path, folder=True):
    songs = file_reader.get_songs_in_folder(os.path.abspath(folder_path)) if folder else [ file_reader.process_file(os.path.abspath(folder_path)) ]
    for song in songs:
        track = bridge.get_song_info(song.meta.title, song.meta.artist, song.meta.album)
        # print(f"Song info: {track}")
        bridge.replace_song(song, track)

def get_played_time():
    days, hours, minutes, seconds, original_minutes = bridge.get_formatted_total_playtime()
    print(f"{math.floor(days)} days, {math.floor(hours)} hrs, {math.floor(minutes)} mins, {math.floor(seconds)} seconds ({math.floor(original_minutes)} minutes)")

def get_stat():
    total_play_time, track_count = bridge.get_total_playtime()
    days, hours, minutes, seconds, original_minutes = bridge.format_time_in_days(total_play_time)
    print(f"You have {track_count} songs in your library")
    print(f"You've listened for {math.floor(days)} days, {math.floor(hours)} hrs, {math.floor(minutes)} mins, {math.floor(seconds)} seconds ({math.floor(original_minutes)} minutes)")

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help']: print_help()
    
    command = sys.argv[1]
    path = sys.argv[2] if len(sys.argv) == 3 else os.getcwd()

    if command == "replace": process_folder(path, folder=os.path.isdir(path))
    elif command == "playedtime": get_played_time()
    elif command == "stat": get_stat()


if __name__ == "__main__":
    main()