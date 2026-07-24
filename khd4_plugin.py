# -*- coding: utf-8 -*-
import urllib.request
import ssl
import re
import traceback
from plugins.metadata.base import BaseMetadataProvider


class Khd4MetadataProvider(BaseMetadataProvider):
    id = "khd4_plugin"
    name = "4KHD 이미지 뷰어"
    is_searchable = False
    
    dashboard_widget = {
        'title': '4KHD 이미지 뷰어',
        'subtitle': '제목과 이미지를 함께 표시하는 갤러리',
        'provider': 'KHD4',
        'icon': 'fa-solid fa-images',
        'limit': 20,
        'all_desk_tab': True,  # 커스텀 뷰어를 전체 화면 탭으로 강제 렌더링
        'supported_types': ['adult', 'general'],
    }

    config_schema = [
        {
            "key": "BASE_URL",
            "label": "갤러리 사이트 주소",
            "type": "text",
            "default": "https://kmngw.uuss.uk",
            "required": True,
            "description": "접속할 갤러리 사이트 주소입니다."
        }
    ]

    def _get_base_url(self, db_type):
        base_url = "https://kmngw.uuss.uk"
        try:
            config = self.get_plugin_config(db_type, default={})
            if isinstance(config, dict):
                val = config.get('BASE_URL')
                if val:
                    base_url = val.strip().rstrip('/')
        except Exception:
            pass
        return base_url

    def search(self, db_type, query):
        return {'success': True, 'items': []}

    def apply(self, db_type, book_id, item_data):
        return False, "대시보드 전용 뷰어 플러그인입니다."

    def _fetch_images(self, base_url, limit=20):
        results = []
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Connection': 'close'
        }
        try:
            req = urllib.request.Request(base_url, headers=headers)
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            with urllib.request.urlopen(req, timeout=15, context=context) as response:
                html_text = response.read().decode('utf-8', errors='ignore')
                posts = re.findall(r'<li[^>]*class="[^"]*wp-block-post[^"]*"[\s\S]*?</li>', html_text)

                for post_html in posts[:limit]:
                    img_match = re.search(r'<img[^>]+(?:src|data-src|data-lazy-src)="([^"]+)"', post_html)
                    img_url = img_match.group(1) if img_match else ""

                    # 제목 추출 정규식
                    title_match = re.search(r'<h2[^>]*class="[^"]*wp-block-post-title[^"]*"[\s\S]*?<a[^>]+href="([^"]+)"[^>]*>([\s\S]*?)<\/a>', post_html)
                    if title_match:
                        link = title_match.group(1)
                        title = re.sub(r'<[^>]+>', '', title_match.group(2)).strip()
                    else:
                        title = "제목 없음"
                        link = ""

                    if img_url:
                        results.append({
                            'title': title,      # 실제 제목 반영
                            'author': '4KHD',    # 저자 미상 방지용
                            'publisher': 'Gallery', # 출판사 미상 방지용
                            'cover': img_url,
                            'cover_url': img_url,
                            'link': link
                        })
        except Exception as e:
            print(f"[Khd4MetadataProvider] 목록 수집 에러: {e}")
        return results

    def _fetch_detail_images(self, detail_url):
        results = []
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Connection': 'close'
        }
        try:
            req = urllib.request.Request(detail_url, headers=headers)
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            with urllib.request.urlopen(req, timeout=15, context=context) as response:
                html_text = response.read().decode('utf-8', errors='ignore')
                example_match = re.search(r'<div[^>]+id="basicExample"[^>]*>([\s\S]*?)<\/div>', html_text)
                target_html = example_match.group(1) if example_match else html_text

                img_matches = re.findall(r'<img[^>]+(?:src|data-src|data-lazy-src)="([^"]+)"', target_html)
                for img_url in img_matches:
                    if img_url:
                        results.append({'cover_url': img_url})
        except Exception as e:
            print(f"[Khd4MetadataProvider] 상세 페이지 수집 에러: {e}")
        return results

    def get_dashboard_data(self, db_type, limit=20):
        base_url = self._get_base_url(db_type)
        items = self._fetch_images(base_url, limit=limit)
        return {
            'success': True,
            'items': items
        }
