# -*- coding: utf-8 -*-
import urllib.request
import json
import ssl
from plugins.metadata.base import BaseMetadataProvider

class Khd4MetadataProvider(BaseMetadataProvider):
    id = "khd4_plugin"
    name = "4KHD 이미지 뷰어"
    is_searchable = False
    
    # 📌 좌측 사이드바 카테고리 메뉴 등록 규격
    category_tab = {
        "title": "4KHD 갤러리",
        "icon": "fa-solid fa-images",
        "order": 80
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

    def get_dashboard_data(self, db_type, limit=50):
        # 1. 설정값 불러오기
        config = self.get_plugin_config(db_type, default={})
        gas_url = config.get('GAS_URL', "https://script.google.com/macros/s/AKfycbyA9t18jOvbUUUKJeMx31B5XAdqwNo-t-m5XuQg3qzuKiwgJNeZLHAB_PEJWP0eWt3Egg/exec")
        base_url = config.get('BASE_URL', "https://fzfqy.uuss.uk")

        full_api_url = f"{gas_url}?base_url={base_url}"

        results = []
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            with urllib.request.urlopen(full_api_url, timeout=30, context=context) as response:
                data = json.loads(response.read().decode('utf-8'))

                if 'images' in data:
                    for img_url in data['images'][:limit]:
                        results.append({
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

    def search(self, db_type, query):
        return {'success': True, 'items': []}

    def apply(self, db_type, book_id, item_data):
        return False, "갤러리 전용 플러그인입니다."