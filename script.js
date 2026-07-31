document.addEventListener('DOMContentLoaded', () => {
    loadKhd4Images();

    const refreshBtn = document.getElementById('khd4-refresh-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            loadKhd4Images();
        });
    }
});

async function loadKhd4Images() {
    const gridContainer = document.getElementById('khd4-gallery-grid');
    if (!gridContainer) return;

    gridContainer.innerHTML = '<div class="khd4-loading">이미지를 불러오는 중입니다...</div>';

    try {
        // 📌 BookOasis 카테고리/위젯 플러그인 데이터 엔드포인트 규격에 맞게 수정
        // 현재 활성화된 라이브러리/DB 타입(general 또는 adult)을 파라미터로 포함하거나 표준 위젯 데이터를 호출합니다.
        const dbType = window.CURRENT_DB_TYPE || 'general'; // 코어 전역 변수나 기본값 활용
        const response = await fetch(`/api/metadata/plugin/data?plugin_id=khd4_plugin&db_type=${dbType}`);
        
        // 만약 위 경로로 안 될 경우를 대비해 플러그인 고유 라우트 엔드포인트 확인
        let result;
        if (response.ok) {
            result = await response.json();
        } else {
            // 대체 경로 시도 (코어 버전에 따른 대시보드 데이터 API 연동)
            const altResponse = await fetch(`/api/plugins/metadata/dashboard/khd4_plugin?db_type=${dbType}`);
            result = await altResponse.json();
        }

        if (result && (result.success || result.items)) {
            const items = result.items || [];
            if (items.length > 0) {
                gridContainer.innerHTML = '';
                
                items.forEach(item => {
                    const card = document.createElement('div');
                    card.className = 'khd4-card';
                    
                    const img = document.createElement('img');
                    // cover_url 또는 cover 필드 모두 대응
                    img.src = item.cover_url || item.cover;
                    img.alt = "4KHD Image";
                    img.loading = "lazy";
                    
                    // 이미지 로드 실패 시 대체 처리
                    img.onerror = function() {
                        this.style.display = 'none';
                    };
                    
                    card.addEventListener('click', () => {
                        const targetLink = item.link || item.source_url;
                        if (targetLink) {
                            window.open(targetLink, '_blank');
                        }
                    });

                    card.appendChild(img);
                    gridContainer.appendChild(card);
                });
                return;
            }
        }
        
        gridContainer.innerHTML = `<div class="khd4-loading">불러올 이미지가 없습니다. (응답 데이터 없음)</div>`;

    } catch (error) {
        console.error('KHD4 갤러리 로딩 실패:', error);
        gridContainer.innerHTML = `<div class="khd4-loading">데이터 통신 중 오류가 발생했습니다: ${error.message}</div>`;
    }
}