import pandas as pd
from TiktokApi import TiktokApi
import time
from datetime import datetime
import os

def preview_csv(file_path, n=10):
    """Hiển thị n dòng đầu tiên của file CSV"""
    try:
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        print("\n=== 10 dòng đầu tiên của dữ liệu ===")
        print(df.head(n))
        print("\nTổng số dòng:", len(df))
    except Exception as e:
        print(f"Lỗi khi đọc file CSV: {e}")

def save_to_csv(comments, output_file=None):
    if not output_file:
        # Tạo thư mục output nếu chưa tồn tại
        if not os.path.exists('output'):
            os.makedirs('output')
        # Tạo tên file với timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f'output/comments_{timestamp}.csv'

    try:
        df = pd.DataFrame(comments)
        columns = {
            'username': 'Tên người dùng',
            'nickname': 'Nickname',
            'bio': 'Tiểu sử',
            'text': 'Nội dung comment'
        }
        
        df = df.rename(columns=columns)
        column_order = ['Tên người dùng', 'Nickname', 'Tiểu sử', 'Nội dung comment']
        df = df[column_order]
        
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f'\nĐã lưu {len(comments)} comments vào file {output_file}')
        
        # Preview dữ liệu sau khi lưu
        preview_csv(output_file)
        
        # Mở thư mục chứa file
        os.startfile(os.path.dirname(os.path.abspath(output_file)))
        
    except Exception as e:
        print(f"Lỗi khi lưu file CSV: {e}")

def main():
    print("=== TikTok Comment Crawler ===")
    video_url = input("\nNhập URL video TikTok: ")
    
    tiktok = TiktokApi()
    video_id = tiktok.extract_video_id(video_url)
    
    if not video_id:
        print("Không thể trích xuất video ID từ URL")
        input("\nNhấn Enter để thoát...")
        return

    all_comments = []
    cursor = 0
    has_more = True
    retry_count = 0
    max_retries = 3
    
    try:
        while has_more and retry_count < max_retries:
            print(f'Đang lấy comments... (Hiện có: {len(all_comments)})')
            result = tiktok.get_video_comments(video_id, cursor)
            
            if not result:
                retry_count += 1
                print(f"Lần thử {retry_count}/{max_retries}")
                time.sleep(5)
                continue

            retry_count = 0
            all_comments.extend(result['comments'])
            cursor = result['cursor']
            has_more = result['has_more']
            
            if len(all_comments) >= 1000:
                break
                
            time.sleep(2)

    except KeyboardInterrupt:
        print("\nĐã dừng thu thập dữ liệu theo yêu cầu của người dùng")
    except Exception as e:
        print(f"Lỗi không xác định trong main: {e}")
    
    if all_comments:
        save_to_csv(all_comments)
    else:
        print("Không tìm thấy comments nào")
    
    input("\nNhấn Enter để thoát...")

if __name__ == '__main__':
    main()