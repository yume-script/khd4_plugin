# -*- coding: utf-8 -*-
import urllib.request
import json
import ssl
from plugins.metadata.base import BaseMetadataProvider

class Khd4MetadataProvider(BaseMetadataProvider):
    id = "khd4_plugin"
    name = "4KHD 이미지 뷰어"
    is_searchable = False
    
    dashboard_widget = {
        'title': '4KHD 이미지 뷰어',
        'subtitle': '4KHD 최신 랜덤 갤러리',
        'provider': 'KHD4',
        'icon': 'fa-solid fa-images',
        'limit': 20,
        'all_desk_tab': True,
        'supported_types': ['adult', 'general'],
    }

    config_schema = [
        {
            "key": "GAS_URL",
            "label": "구글 앱스 스크립트 배포 URL",
            "type": "text",
            "default": "https://script.google.com/macros/s/AKfycbyA9t18jOvbUUUKJeMx31B5XAdqwNo-t-m5XuQg3qzuKiwgJNeZLHAB_PEJWP0eWt3Egg/exec",
            "required": True,
            "description": "파싱을 수행하는 구글 앱스 스크립트 주소입니다."
        },
        {
            "key": "BASE_URL",
            "label": "갤러리 사이트 주소",
            "type": "text",
            "default": "https://fzfqy.uuss.uk",
            "required": True,
            "description": "실제 이미지 갤러리 사이트 주소입니다."
        }
    ]
    def get_dashboard_data(self, db_type, limit=20):
        # 1. 설정값 불러오기
        config = self.get_plugin_config(db_type, default={})
        gas_url = config.get('GAS_URL', "https://script.google.com/macros/s/AKfycbyA9t18jOvbUUUKJeMx31B5XAdqwNo-t-m5XuQg3qzuKiwgJNeZLHAB_PEJWP0eWt3Egg/exec")
        base_url = config.get('BASE_URL', "https://fzfqy.uuss.uk")

        # 2. 파라미터 조합
        full_api_url = f"{gas_url}?base_url={base_url}"

        results = []
        try:
            # 3. 구글 앱스 스크립트를 통해 JSON 데이터 수집
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            with urllib.request.urlopen(full_api_url, timeout=30, context=context) as response:
                data = json.loads(response.read().decode('utf-8'))

                # 4. 수집된 데이터(images 리스트)를 대시보드 아이템 형식으로 변환
                if 'images' in data:
                    for img_url in data['images'][:limit]:
                        results.append({
                            'title': '4KHD 이미지',
                            'author': '4KHD',
                            'publisher': 'Gallery',
                            'cover': img_url,
                            'cover_url': img_url,
                            'link': data.get('source_url', base_url)
                        })
        except Exception as e:
            print(f"[Khd4MetadataProvider] 데이터 수집 에러: {e}")
            return {'success': False, 'message': str(e)}

        return {
            'success': True,
            'items': results
        }
    # 대시보드 뷰어 플러그인이므로 검색 및 apply는 기본값 유지
    def search(self, db_type, query):
        return {'success': True, 'items': []}

    def apply(self, db_type, book_id, item_data):
        return False, "대시보드 전용 뷰어 플러그인입니다."
