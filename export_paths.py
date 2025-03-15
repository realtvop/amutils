#!/usr/bin/env python3
"""
导出 Apple Music 库中所有曲目的文件路径到 txt 文件。
这可以帮助用户识别和匹配他们的音乐文件路径。
"""

import os
import sys
import bridge

def export_paths_to_txt(output_path):
    """
    将所有曲目的文件路径导出到文本文件。

    Args:
        output_path (str): 保存文本文件的路径

    Returns:
        bool: 导出成功返回 True，否则返回 False
    """
    try:
        # 获取所有曲目
        tracks = bridge.get_all_tracks()
        
        if not tracks:
            print("库中没有找到曲目。")
            return False
            
        # 过滤出有文件路径的曲目
        tracks_with_paths = [track for track in tracks if track.file_path]
        
        if not tracks_with_paths:
            print("未找到带有文件路径的曲目。")
            return False
            
        # 按文件路径排序
        tracks_with_paths.sort(key=lambda x: x.file_path)
        
        # 写入文本文件
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                # 写入文件头
                f.write("# Apple Music 曲库文件路径\n")
                f.write("# 总数: {} 个文件\n".format(len(tracks_with_paths)))
                f.write("# 格式: 文件路径 | 曲名 | 艺术家\n\n")
                
                for track in tracks_with_paths:
                    # 写入格式: 文件路径 | 曲名 | 艺术家
                    f.write(f"{track.file_path} | {track.name} | {track.artist}\n")
                    
            print(f"成功导出 {len(tracks_with_paths)} 个文件路径到 {output_path}")
            return True
        except Exception as e:
            print(f"写入文件时出错: {e}")
            return False
            
    except Exception as e:
        print(f"导出路径时出错: {e}")
        return False

def main():
    """主函数，处理命令行参数并运行程序"""
    # 检查参数
    if len(sys.argv) < 2:
        print("用法: python3 export_paths.py <输出路径.txt>")
        return
        
    output_path = sys.argv[1]
    
    # 确保文件扩展名是 .txt
    if not output_path.endswith('.txt'):
        output_path += '.txt'
    
    # 导出路径
    export_paths_to_txt(output_path)

if __name__ == "__main__":
    main()
