import PyInstaller.__main__
import os

# Tạo thư mục dist nếu chưa tồn tại
if not os.path.exists('dist'):
    os.makedirs('dist')

PyInstaller.__main__.run([
    'main.py',
    '--onefile',
    '--name=TikTok_Comment_Crawler',
    '--add-data=TiktokApi.py;.',
    '--clean'
]) 