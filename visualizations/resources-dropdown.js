// Resources Dropdown Navigation JavaScript

(function () {
    'use strict';

    // Initialize dropdown when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initResourcesDropdown);
    } else {
        initResourcesDropdown();
    }

    function initResourcesDropdown() {
        const dropdown = document.querySelector('.nav-dropdown');
        if (!dropdown) return;

        const toggle = dropdown.querySelector('.nav-dropdown-toggle');
        const menu = dropdown.querySelector('.nav-dropdown-menu');
        const comparisonToggle = dropdown.querySelector('.comparison-toggle');
        const comparisonContent = dropdown.querySelector('.comparison-content');

        // Show dropdown on hover (mouseenter)
        if (dropdown) {
            dropdown.addEventListener('mouseenter', function (e) {
                openDropdown();
            });

            // Hide dropdown on mouse leave
            dropdown.addEventListener('mouseleave', function (e) {
                closeDropdown();
            });
        }

        // Click/tap support for toggle (mobile & accessibility)
        if (toggle) {
            toggle.addEventListener('click', function (e) {
                e.stopPropagation();
                toggleDropdown();
            });

            toggle.addEventListener('keydown', function (e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    toggleDropdown();
                } else if (e.key === 'Escape') {
                    closeDropdown();
                }
            });
        }

        // Close dropdown when tapping outside on mobile
        document.addEventListener('click', function (e) {
            if (!dropdown.contains(e.target)) {
                closeDropdown();
            }
        });

        // Toggle comparison table
        if (comparisonToggle) {
            comparisonToggle.addEventListener('click', function (e) {
                e.stopPropagation();
                comparisonToggle.classList.toggle('open');
                comparisonContent.classList.toggle('open');
            });
        }

        // Close dropdown on Escape key
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                closeDropdown();
            }
        });

        // Keyboard navigation for jurisdiction cards
        const jurisdictionCards = dropdown.querySelectorAll('.jurisdiction-card');
        jurisdictionCards.forEach(function (card, index) {
            card.addEventListener('keydown', function (e) {
                if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    const next = jurisdictionCards[index + 1];
                    if (next) next.focus();
                } else if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    const prev = jurisdictionCards[index - 1];
                    if (prev) prev.focus();
                } else if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    card.click();
                }
            });
        });

        function toggleDropdown() {
            const isOpen = dropdown.classList.contains('open');
            if (isOpen) {
                closeDropdown();
            } else {
                openDropdown();
            }
        }

        function openDropdown() {
            dropdown.classList.add('open');
            toggle.setAttribute('aria-expanded', 'true');
            menu.setAttribute('aria-hidden', 'false');

            // Position dropdown using fixed positioning relative to toggle button
            positionDropdown();

            // Focus first jurisdiction card
            const firstCard = dropdown.querySelector('.jurisdiction-card');
            if (firstCard) {
                setTimeout(function () {
                    firstCard.focus();
                }, 100);
            }
        }

        function positionDropdown() {
            if (!toggle || !menu) return;

            // Get toggle button position relative to viewport
            const toggleRect = toggle.getBoundingClientRect();
            const isMobile = window.innerWidth <= 768;
            
            if (isMobile) {
                // Mobile: center the dropdown horizontally
                const top = toggleRect.bottom + 0.5 * 16; // 0.5rem = 8px
                const left = (window.innerWidth - menu.offsetWidth) / 2;
                
                menu.style.top = top + 'px';
                menu.style.left = Math.max(16, left) + 'px'; // Ensure 16px margin
            } else {
                // Desktop: position below toggle button
                const top = toggleRect.bottom + 0.5 * 16; // 0.5rem = 8px
                const left = toggleRect.left;

                // Set dropdown position
                menu.style.top = top + 'px';
                menu.style.left = left + 'px';

                // Adjust if dropdown would overflow viewport
                // Force a reflow to get accurate dimensions
                menu.style.visibility = 'hidden';
                menu.style.opacity = '0';
                const menuRect = menu.getBoundingClientRect();
                menu.style.visibility = '';
                menu.style.opacity = '';
                
                const viewportWidth = window.innerWidth;
                const viewportHeight = window.innerHeight;

                // Check right edge overflow
                if (menuRect.right > viewportWidth) {
                    menu.style.left = (viewportWidth - menuRect.width - 16) + 'px'; // 16px margin
                }

                // Check left edge overflow
                if (menuRect.left < 0) {
                    menu.style.left = '16px'; // 16px margin
                }

                // Check bottom edge overflow
                if (menuRect.bottom > viewportHeight) {
                    // Position above the toggle button instead
                    menu.style.top = (toggleRect.top - menuRect.height - 0.5 * 16) + 'px';
                }
            }
        }

        // Reposition dropdown on scroll or resize
        window.addEventListener('scroll', function() {
            if (dropdown.classList.contains('open')) {
                positionDropdown();
            }
        }, { passive: true });

        window.addEventListener('resize', function() {
            if (dropdown.classList.contains('open')) {
                positionDropdown();
            }
        });

        function closeDropdown() {
            dropdown.classList.remove('open');
            toggle.setAttribute('aria-expanded', 'false');
            menu.setAttribute('aria-hidden', 'true');
        }
    }

    // Jurisdiction click handlers - navigate to legal guides page with hash
    function openJurisdictionModal(jurisdiction) {
        // Navigate to the legal guides page with the specific jurisdiction hash
        window.location.href = 'legal_guides.html#' + jurisdiction;
    }

    // Make function available globally
    window.openJurisdictionModal = openJurisdictionModal;
})();
