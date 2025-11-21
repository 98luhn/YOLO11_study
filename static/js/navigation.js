/**
 * Navigation Enhancement for YOLO11 Multi-Layer Detection System
 * 모바일 햄버거 메뉴 및 로고 홈 링크 기능
 * Created: 2025-11-21
 */

// 네비게이션 초기화
function initNavigation() {
    // 로고를 홈 링크로 만들기
    const navBrand = document.querySelector('.nav-brand');
    if (navBrand && !navBrand.closest('a')) {
        // 현재 페이지 확인
        const isHomePage = window.location.pathname === '/' || 
                          window.location.pathname.endsWith('index.html') ||
                          window.location.pathname === '/yolo11_detector/' ||
                          window.location.pathname === '/YOLO11_study/';
        
        // 로고를 클릭 가능한 링크로 변환
        const brandLink = document.createElement('a');
        brandLink.href = isHomePage ? '#' : 'index.html';
        brandLink.className = 'nav-brand-link';
        brandLink.style.textDecoration = 'none';
        brandLink.style.color = 'inherit';
        brandLink.style.display = 'flex';
        brandLink.style.alignItems = 'center';
        brandLink.style.gap = '0.5rem';
        
        // 기존 로고 내용을 링크로 이동
        brandLink.innerHTML = navBrand.innerHTML;
        navBrand.innerHTML = '';
        navBrand.appendChild(brandLink);
        
        // 홈페이지가 아닐 때만 클릭 이벤트 추가
        if (!isHomePage) {
            brandLink.style.cursor = 'pointer';
        }
    }
    
    // 햄버거 메뉴 추가
    createMobileMenu();
}

// 모바일 햄버거 메뉴 생성
function createMobileMenu() {
    const navbar = document.querySelector('.navbar');
    const navMenu = document.querySelector('.nav-menu');
    
    if (!navbar || !navMenu) return;
    
    // 햄버거 버튼 생성
    const hamburger = document.createElement('button');
    hamburger.className = 'nav-hamburger';
    hamburger.innerHTML = `
        <span class="hamburger-line"></span>
        <span class="hamburger-line"></span>
        <span class="hamburger-line"></span>
    `;
    hamburger.setAttribute('aria-label', '메뉴');
    hamburger.setAttribute('aria-expanded', 'false');
    
    // 네비게이션 바에 햄버거 추가
    const container = navbar.querySelector('.container');
    if (container) {
        // nav-brand 다음에 햄버거 버튼 삽입
        const navBrand = container.querySelector('.nav-brand');
        if (navBrand) {
            navBrand.parentNode.insertBefore(hamburger, navMenu);
        }
    }
    
    // 햄버거 클릭 이벤트
    hamburger.addEventListener('click', () => {
        const isOpen = navMenu.classList.contains('show');
        navMenu.classList.toggle('show');
        hamburger.classList.toggle('active');
        hamburger.setAttribute('aria-expanded', !isOpen);
        
        // 메뉴가 열릴 때 body 스크롤 방지
        document.body.style.overflow = isOpen ? '' : 'hidden';
    });
    
    // 메뉴 항목 클릭 시 모바일 메뉴 닫기
    const navLinks = navMenu.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            if (window.innerWidth <= 768) {
                navMenu.classList.remove('show');
                hamburger.classList.remove('active');
                hamburger.setAttribute('aria-expanded', 'false');
                document.body.style.overflow = '';
            }
        });
    });
    
    // 창 크기 변경 시 메뉴 초기화
    let resizeTimer;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            if (window.innerWidth > 768) {
                navMenu.classList.remove('show');
                hamburger.classList.remove('active');
                hamburger.setAttribute('aria-expanded', 'false');
                document.body.style.overflow = '';
            }
        }, 250);
    });
    
    // CSS 스타일 추가
    if (!document.getElementById('nav-mobile-styles')) {
        const style = document.createElement('style');
        style.id = 'nav-mobile-styles';
        style.textContent = `
            /* 햄버거 메뉴 스타일 */
            .nav-hamburger {
                display: none;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                width: 40px;
                height: 40px;
                padding: 0;
                background: transparent;
                border: none;
                cursor: pointer;
                z-index: 1001;
            }
            
            .hamburger-line {
                display: block;
                width: 25px;
                height: 3px;
                background: var(--gray-700);
                border-radius: 3px;
                transition: all 0.3s ease;
                margin: 3px 0;
            }
            
            .nav-hamburger.active .hamburger-line:nth-child(1) {
                transform: rotate(45deg) translate(6px, 6px);
            }
            
            .nav-hamburger.active .hamburger-line:nth-child(2) {
                opacity: 0;
            }
            
            .nav-hamburger.active .hamburger-line:nth-child(3) {
                transform: rotate(-45deg) translate(7px, -6px);
            }
            
            /* 모바일 반응형 */
            @media (max-width: 768px) {
                .nav-hamburger {
                    display: flex;
                    margin-left: auto;
                }
                
                .navbar .container {
                    position: relative;
                }
                
                .nav-menu {
                    position: fixed;
                    top: 60px;
                    left: 0;
                    right: 0;
                    background: white;
                    flex-direction: column;
                    padding: 1rem;
                    box-shadow: var(--shadow-lg);
                    transform: translateY(-100%);
                    opacity: 0;
                    visibility: hidden;
                    transition: all 0.3s ease;
                    z-index: 1000;
                    max-height: calc(100vh - 60px);
                    overflow-y: auto;
                }
                
                .nav-menu.show {
                    transform: translateY(0);
                    opacity: 1;
                    visibility: visible;
                }
                
                .nav-menu .nav-link {
                    display: block;
                    padding: 0.75rem 1rem;
                    margin: 0.25rem 0;
                    border-radius: 0.5rem;
                    width: 100%;
                    text-align: left;
                }
                
                .nav-menu .theme-selector {
                    width: 100%;
                    margin: 0.25rem 0;
                }
                
                .nav-menu .theme-toggle {
                    width: 100%;
                    justify-content: flex-start;
                    padding: 0.75rem 1rem;
                }
                
                .theme-label {
                    display: inline !important;
                }
                
                /* 로고 조정 */
                .nav-brand {
                    flex: 1;
                }
                
                .nav-brand-link {
                    font-size: 1.125rem;
                }
            }
            
            /* 로고 호버 효과 */
            .nav-brand-link:hover {
                opacity: 0.8;
                transition: opacity 0.2s ease;
            }
            
            /* 테마 버튼 크기 통일 */
            .theme-toggle {
                font-size: 0.9rem !important;
                font-weight: 500 !important;
                padding: 0.5rem 1rem !important;
            }
        `;
        document.head.appendChild(style);
    }
}

// DOM 로드 시 초기화
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initNavigation);
} else {
    initNavigation();
}