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

        // Toggle dropdown on click
        if (toggle) {
            toggle.addEventListener('click', function (e) {
                e.preventDefault();
                e.stopPropagation();
                toggleDropdown();
            });

            // Keyboard support for toggle
            toggle.addEventListener('keydown', function (e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    toggleDropdown();
                } else if (e.key === 'Escape') {
                    closeDropdown();
                }
            });
        }

        // Toggle comparison table
        if (comparisonToggle) {
            comparisonToggle.addEventListener('click', function (e) {
                e.stopPropagation();
                comparisonToggle.classList.toggle('open');
                comparisonContent.classList.toggle('open');
            });
        }

        // Close dropdown when clicking outside
        document.addEventListener('click', function (e) {
            if (!dropdown.contains(e.target)) {
                closeDropdown();
            }
        });

        // Close dropdown on Escape key
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                closeDropdown();
            }
        });

        // Prevent dropdown from closing when clicking inside
        if (menu) {
            menu.addEventListener('click', function (e) {
                e.stopPropagation();
            });
        }

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

            // Focus first jurisdiction card
            const firstCard = dropdown.querySelector('.jurisdiction-card');
            if (firstCard) {
                setTimeout(function () {
                    firstCard.focus();
                }, 100);
            }
        }

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
