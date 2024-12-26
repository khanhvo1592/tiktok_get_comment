import requests
import re
import time
import json

class TiktokApi():
    def __init__(self):
        self.tiktok_api_url = 'https://api16-normal-c-useast1a.tiktokv.com/aweme/v1'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def extract_video_id(self, url: str) -> str:
        """Trích xuất video ID từ URL TikTok"""
        pattern = r'/video/(\d+)'
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        return None

    def get_user_info(self, username: str):
        """Lấy thông tin chi tiết của người dùng"""
        url = f'{self.tiktok_api_url}/user/detail/'
        params = {
            'unique_id': username,
            'language': 'vi'
        }

        try:
            res = requests.get(url, params=params, headers=self.headers)
            if res.status_code != 200:
                print(f'Không thể lấy thông tin user {username}. Status Code: {res.status_code}')
                return None

            user_info = res.json().get('user', {})
            return {
                'user_id': user_info.get('uid', ''),
                'nickname': user_info.get('nickname', ''),
                'avatar': user_info.get('avatar_larger', {}).get('url_list', [''])[0],
                'bio': user_info.get('signature', '')
            }
        except Exception as err:
            print(f"Lỗi khi lấy thông tin user {username}: {err}")
            return None

    def get_video_comments(self, video_id: str, cursor: int = 0, count: int = 50):
        """Lấy comments của video"""
        url = f'{self.tiktok_api_url}/comment/list/'
        params = {
            'aweme_id': video_id,
            'cursor': cursor,
            'count': count
        }

        try:
            print(f"Đang gửi request đến: {url}")
            res = requests.get(url, params=params, headers=self.headers)
            
            print(f"Status Code: {res.status_code}")
            if res.status_code != 200:
                print(f"Response error: {res.text}")
                return None

            try:
                res_json = res.json()
            except json.JSONDecodeError as e:
                print(f"Lỗi parse JSON: {e}")
                print(f"Response content: {res.text[:200]}...")
                return None

            if not res_json:
                print("Response rỗng")
                return None

            comments = res_json.get('comments', [])
            has_more = res_json.get('has_more', 0)
            cursor = res_json.get('cursor', 0)

            if not comments:
                print("Không tìm thấy comments trong response")
                return None

            results = []
            for comment in comments:
                try:
                    user = comment.get('user', {})
                    results.append({
                        'username': user.get('unique_id', ''),
                        'nickname': user.get('nickname', ''),
                        'bio': user.get('signature', ''),
                        'text': comment.get('text', '')
                    })
                except Exception as comment_err:
                    print(f"Lỗi xử lý comment: {comment_err}")
                    continue

            return {
                'comments': results,
                'cursor': cursor,
                'has_more': has_more
            }

        except requests.exceptions.RequestException as err:
            print(f"Lỗi request: {err}")
            return None
        except Exception as err:
            print(f"Lỗi không xác định: {err}")
            return None