/**
 * Theme handling for light/dark mode switching
 */
document.addEventListener('DOMContentLoaded', () => {
    // Theme toggler with improved transition
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = themeToggle.querySelector('i');
    const currentTheme = localStorage.getItem('theme');
    
    // Set initial theme
    if (currentTheme === 'dark') {
        document.body.classList.add('dark-mode');
        themeIcon.classList.replace('fa-moon', 'fa-sun');
        
        // Apply dark mode to main nav if on mobile
        const mainNav = document.querySelector('.main-nav');
        if (window.innerWidth <= 768 && mainNav) {
            mainNav.style.backgroundColor = '#1e293b';
            mainNav.style.borderTopColor = '#334155';
        }
        
        // Apply text colors if dark mode is active on page load
        const textElements = document.querySelectorAll('h1, h2, h3, h4, h5, h6, p, span, label, .car-title a, .info-value, .car-detail, .car-meta, .car-seller');
        
        textElements.forEach(element => {
            if (element.classList.contains('heading') || 
                element.tagName.match(/^H[1-6]$/)) {
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
        });
        
        // Fix car title links specifically
        const carTitleLinks = document.querySelectorAll('.car-title a');
        carTitleLinks.forEach(link => {
            link.style.color = 'var(--heading-color)';
        });
    }
    
    // Theme toggle with event dispatching
    themeToggle.addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
        const isDarkMode = document.body.classList.contains('dark-mode');
        localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
        
        // Update mobile nav styling when toggling theme
        const mainNav = document.querySelector('.main-nav');
        if (window.innerWidth <= 768 && mainNav) {
            if (isDarkMode) {
                mainNav.style.backgroundColor = '#1e293b';
                mainNav.style.borderTopColor = '#334155';
            } else {
                mainNav.style.backgroundColor = '#ffffff';
                mainNav.style.borderTopColor = '#e2e8f0';
            }
        }
        
        if (isDarkMode) {
            themeIcon.classList.replace('fa-moon', 'fa-sun');
        } else {
            themeIcon.classList.replace('fa-sun', 'fa-moon');
        }
        
        // Fix color transitions for text elements that might not update properly
        const textElements = document.querySelectorAll('h1, h2, h3, h4, h5, h6, p, span, label, .car-title a, .info-value, .car-detail, .car-meta, .car-seller');
        
        textElements.forEach(element => {
            // Force a repaint to ensure color transition applies
            element.style.transition = 'none';
            element.offsetHeight; // Trigger a reflow
            element.style.transition = '';
            
            // Apply appropriate color based on theme
            if (isDarkMode) {
                if (element.classList.contains('heading') || 
                    element.tagName.match(/^H[1-6]$/)) {
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
                // Reset to default theme colors
                element.style.color = '';
            }
        });
        
        // Fix car title links specifically
        const carTitleLinks = document.querySelectorAll('.car-title a');
        carTitleLinks.forEach(link => {
            link.style.color = isDarkMode ? 'var(--heading-color)' : '';
        });
        
        // Dispatch event for other scripts that might need to react
        const event = new CustomEvent('themeChanged', {
            detail: { theme: isDarkMode ? 'dark' : 'light' }
        });
        document.dispatchEvent(event);
    });
    
    // Mobile menu with improved animation and accessibility
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const mainNav = document.querySelector('.main-nav');
    
    if (mobileMenuToggle && mainNav) {
        mobileMenuToggle.setAttribute('aria-expanded', 'false');
        mobileMenuToggle.setAttribute('aria-controls', 'main-navigation');
        mainNav.setAttribute('id', 'main-navigation');
        
        mobileMenuToggle.addEventListener('click', (e) => {
            e.stopPropagation(); // Prevent event bubbling
            const isExpanded = mobileMenuToggle.classList.toggle('active');
            mainNav.classList.toggle('active');
            mobileMenuToggle.setAttribute('aria-expanded', isExpanded ? 'true' : 'false');
            
            // Apply correct styling based on theme when menu is toggled
            if (mainNav.classList.contains('active')) {
                if (document.body.classList.contains('dark-mode')) {
                    mainNav.style.backgroundColor = '#1e293b';
                    mainNav.style.borderTopColor = '#334155';
                } else {
                    mainNav.style.backgroundColor = '#ffffff';
                    mainNav.style.borderTopColor = '#e2e8f0';
                }
            }
        });
        
        // Close mobile menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.mobile-menu-toggle') && !e.target.closest('.main-nav')) {
                mainNav.classList.remove('active');
                mobileMenuToggle.classList.remove('active');
                mobileMenuToggle.setAttribute('aria-expanded', 'false');
            }
        });
    }
    
    // User dropdown
    const userDropdownToggle = document.querySelector('.user-dropdown-toggle');
    const userDropdownMenu = document.querySelector('.user-dropdown-menu');
    
    if (userDropdownToggle && userDropdownMenu) {
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
    
    // Close messages
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
    
    // Fix for logout button style
    const logoutButton = document.querySelector('form[action*="logout"] button');
    if (logoutButton) {
        logoutButton.classList.add('dropdown-item-button');
        
        // Apply correct styling based on current theme
        if (document.body.classList.contains('dark-mode')) {
            logoutButton.style.color = '#e2e8f0';
            logoutButton.addEventListener('mouseover', function() {
                this.style.backgroundColor = '#334155';
                this.style.color = '#60a5fa';
            });
            logoutButton.addEventListener('mouseout', function() {
                this.style.backgroundColor = 'transparent';
                this.style.color = '#e2e8f0';
            });
        }
    }
    
    // Handle resize for mobile menu styling
    window.addEventListener('resize', () => {
        if (mainNav) {
            if (window.innerWidth > 768) {
                mainNav.style.backgroundColor = '';
                mainNav.style.borderTopColor = '';
            } else if (mainNav.classList.contains('active')) {
                if (document.body.classList.contains('dark-mode')) {
                    mainNav.style.backgroundColor = '#1e293b';
                    mainNav.style.borderTopColor = '#334155';
                } else {
                    mainNav.style.backgroundColor = '#ffffff';
                    mainNav.style.borderTopColor = '#e2e8f0';
                }
            }
        }
    });
});
