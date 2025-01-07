from appscript import app, its

music = app('Music')

def get_total_playtime():
    try:
        library = music.library_playlists[1]
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

# 调用函数并显示结果
total_seconds = get_total_playtime()
days, hours, minutes, seconds, original_minutes = format_time_in_days(total_seconds)
print(f"音乐库的总播放时长: {days} 天 {hours} 小时 {minutes} 分钟 {seconds} 秒 (分钟: {original_minutes})")
