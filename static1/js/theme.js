/**
 * Theme handling for light/dark mode switching
 * Оптимизированная версия с улучшенной производительностью
 */
document.addEventListener('DOMContentLoaded', () => {
    // Основные элементы для управления темой
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = themeToggle?.querySelector('i');
    const mainNav = document.querySelector('.main-nav');
    const currentTheme = localStorage.getItem('theme');
    
    // Вспомогательная функция для применения темных стилей к навигации
    const applyDarkNavStyles = (nav) => {
        if (window.innerWidth <= 768 && nav) {
            nav.style.backgroundColor = '#1e293b';
            nav.style.borderTopColor = '#334155';
        }
    };
    
    // Вспомогательная функция для применения светлых стилей к навигации
    const applyLightNavStyles = (nav) => {
        if (window.innerWidth <= 768 && nav) {
            nav.style.backgroundColor = '#ffffff';
            nav.style.borderTopColor = '#e2e8f0';
        }
    };
    
    // Вспомогательная функция для обновления текстовых элементов в соответствии с темой
    const updateTextElements = (isDarkMode) => {
        const textElements = document.querySelectorAll('h1, h2, h3, h4, h5, h6, p, span, label, .car-title a, .info-value, .car-detail, .car-meta, .car-seller');
        
        textElements.forEach(element => {
            // Оптимизация: устраняет ненужное мерцание во время смены темы
            element.style.transition = 'none';
            element.offsetHeight; // Trigger a reflow
            element.style.transition = '';
            
            if (isDarkMode) {
                // Применение цветов в зависимости от типа элемента
                if (element.classList.contains('heading') || element.tagName.match(/^H[1-6]$/)) {
                    element.style.color = 'var(--heading-color)';
                } 
                else if (element.classList.contains('text-muted') ||
                         element.classList.contains('car-meta') ||
                         element.classList.contains('car-seller') ||
                         element.classList.contains('info-label')) {
                    element.style.color = 'var(--text-muted)';
                }
                else {
                    element.style.color = 'var(--text-color)';
                }
            } else {
                // Возврат к стандартным цветам для светлой темы
                element.style.color = '';
            }
        });
        
        // Отдельная обработка ссылок в заголовках авто (это часто используемый элемент)
        const carTitleLinks = document.querySelectorAll('.car-title a');
        carTitleLinks.forEach(link => {
            link.style.color = isDarkMode ? 'var(--heading-color)' : '';
        });
    };
    
    // Установка начальной темы
    if (currentTheme === 'dark') {
        document.body.classList.add('dark-mode');
        if (themeIcon) {
            themeIcon.classList.replace('fa-moon', 'fa-sun');
        }
        
        // Применение темных стилей к навигации
        applyDarkNavStyles(mainNav);
        
        // Применение цветов темной темы к текстовым элементам
        updateTextElements(true);
    }
    
    // Обработка переключения темы
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            document.body.classList.toggle('dark-mode');
            const isDarkMode = document.body.classList.contains('dark-mode');
            localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
            
            // Обновление стилей навигации в соответствии с темой
            if (isDarkMode) {
                applyDarkNavStyles(mainNav);
                if (themeIcon) {
                    themeIcon.classList.replace('fa-moon', 'fa-sun');
                }
            } else {
                applyLightNavStyles(mainNav);
                if (themeIcon) {
                    themeIcon.classList.replace('fa-sun', 'fa-moon');
                }
            }
            
            // Обновление текстовых элементов
            updateTextElements(isDarkMode);
            
            // Отправка события о смене темы
            const event = new CustomEvent('themeChanged', {
                detail: { theme: isDarkMode ? 'dark' : 'light' }
            });
            document.dispatchEvent(event);
        });
    }
    
    // Обработка мобильного меню
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    
    if (mobileMenuToggle && mainNav) {
        // Улучшение доступности
        mobileMenuToggle.setAttribute('aria-expanded', 'false');
        mobileMenuToggle.setAttribute('aria-controls', 'main-navigation');
        mainNav.setAttribute('id', 'main-navigation');
        
        mobileMenuToggle.addEventListener('click', (e) => {
            e.stopPropagation(); // Предотвращение всплытия события
            const isExpanded = mobileMenuToggle.classList.toggle('active');
            mainNav.classList.toggle('active');
            mobileMenuToggle.setAttribute('aria-expanded', isExpanded ? 'true' : 'false');
            
            // Применение стилей в зависимости от темы
            if (mainNav.classList.contains('active')) {
                if (document.body.classList.contains('dark-mode')) {
                    applyDarkNavStyles(mainNav);
                } else {
                    applyLightNavStyles(mainNav);
                }
            }
        });
        
        // Закрытие мобильного меню при клике вне области
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.mobile-menu-toggle') && !e.target.closest('.main-nav')) {
                mainNav.classList.remove('active');
                mobileMenuToggle.classList.remove('active');
                mobileMenuToggle.setAttribute('aria-expanded', 'false');
            }
        });
    }
    
    // Выпадающее меню пользователя
    const setupUserDropdown = () => {
        const userDropdownToggle = document.querySelector('.user-dropdown-toggle');
        const userDropdownMenu = document.querySelector('.user-dropdown-menu');
        
        if (userDropdownToggle && userDropdownMenu) {
            // Улучшение доступности
            userDropdownToggle.setAttribute('aria-expanded', 'false');
            userDropdownToggle.setAttribute('aria-controls', 'user-dropdown');
            userDropdownMenu.setAttribute('id', 'user-dropdown');
            
            userDropdownToggle.addEventListener('click', (e) => {
                e.stopPropagation();
                const isExpanded = userDropdownMenu.classList.toggle('active');
                userDropdownToggle.setAttribute('aria-expanded', isExpanded ? 'true' : 'false');
            });
            
            document.addEventListener('click', (e) => {
                if (!e.target.closest('.user-dropdown')) {
                    userDropdownMenu.classList.remove('active');
                    userDropdownToggle.setAttribute('aria-expanded', 'false');
                }
            });
        }
    };
    
    // Закрытие сообщений
    const setupMessageClose = () => {
        const messageCloseButtons = document.querySelectorAll('.message-close');
        messageCloseButtons.forEach(button => {
            button.addEventListener('click', () => {
                const message = button.closest('.message');
                message.style.opacity = '0';
                setTimeout(() => {
                    message.remove();
                }, 300);
            });
        });
    };
    
    // Стилизация кнопки выхода
    const setupLogoutButton = () => {
        const logoutButton = document.querySelector('form[action*="logout"] button');
        if (logoutButton) {
            logoutButton.classList.add('dropdown-item-button');
            
            // Применение стилей в зависимости от темы
            if (document.body.classList.contains('dark-mode')) {
                logoutButton.style.color = '#e2e8f0';
                
                // Использование более эффективного способа привязки обработчиков событий
                const handleMouseOver = function() {
                    this.style.backgroundColor = '#334155';
                    this.style.color = '#60a5fa';
                };
                
                const handleMouseOut = function() {
                    this.style.backgroundColor = 'transparent';
                    this.style.color = '#e2e8f0';
                };
                
                logoutButton.addEventListener('mouseover', handleMouseOver);
                logoutButton.addEventListener('mouseout', handleMouseOut);
            }
        }
    };
    
    // Обработка изменения размера для мобильного меню
    const handleResize = () => {
        if (mainNav) {
            if (window.innerWidth > 768) {
                mainNav.style.backgroundColor = '';
                mainNav.style.borderTopColor = '';
            } else if (mainNav.classList.contains('active')) {
                if (document.body.classList.contains('dark-mode')) {
                    applyDarkNavStyles(mainNav);
                } else {
                    applyLightNavStyles(mainNav);
                }
            }
        }
    };
    
    window.addEventListener('resize', handleResize);
    
    // Инициализация всех компонентов
    setupUserDropdown();
    setupMessageClose();
    setupLogoutButton();
});
