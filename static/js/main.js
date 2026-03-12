// UrbanSafe - Main JavaScript

document.addEventListener('DOMContentLoaded', function () {

    // --- Theme Toggle ---
    const themeToggle = document.getElementById('theme-toggle');
    const iconDark = document.getElementById('theme-icon-dark');
    const iconLight = document.getElementById('theme-icon-light');
    const html = document.documentElement;

    // Load saved theme
    const savedTheme = localStorage.getItem('urbansafe-theme') || 'dark';
    html.setAttribute('data-theme', savedTheme);
    updateThemeIcons(savedTheme);

    if (themeToggle) {
        themeToggle.addEventListener('click', function () {
            const current = html.getAttribute('data-theme');
            const next = current === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-theme', next);
            localStorage.setItem('urbansafe-theme', next);
            updateThemeIcons(next);
        });
    }

    function updateThemeIcons(theme) {
        if (iconDark && iconLight) {
            if (theme === 'dark') {
                iconDark.style.display = 'inline';
                iconLight.style.display = 'none';
            } else {
                iconDark.style.display = 'none';
                iconLight.style.display = 'inline';
            }
        }
    }

    // --- Mobile Nav Toggle ---
    const navToggle = document.getElementById('nav-toggle');
    const navLinks = document.getElementById('nav-links');
    if (navToggle && navLinks) {
        navToggle.addEventListener('click', function () {
            navLinks.classList.toggle('active');
        });
    }

    // --- Auto-dismiss messages ---
    const messages = document.querySelectorAll('.message');
    messages.forEach((msg, index) => {
        setTimeout(() => {
            msg.style.opacity = '0';
            msg.style.transform = 'translateX(40px)';
            setTimeout(() => msg.remove(), 300);
        }, 4000 + (index * 500));
    });

    // --- Alert polling (every 30s) ---
    function pollAlerts() {
        fetch('/api/alerts/unread-count/')
            .then(response => response.json())
            .then(data => {
                const badge = document.getElementById('alert-badge');
                if (badge) {
                    if (data.count > 0) {
                        badge.textContent = data.count;
                        badge.style.display = 'flex';
                    } else {
                        badge.style.display = 'none';
                    }
                }
            })
            .catch(() => { });
    }

    // Poll alerts if user is logged in (badge exists means logged in)
    if (document.getElementById('alert-badge')) {
        pollAlerts();
        setInterval(pollAlerts, 30000);
    }

    // --- Filter form auto-submit ---
    const filterSelects = document.querySelectorAll('.filter-select');
    filterSelects.forEach(select => {
        select.addEventListener('change', function () {
            this.closest('form').submit();
        });
    });

    // --- Geolocation ---
    const getLocationBtn = document.getElementById('get-location-btn');
    if (getLocationBtn) {
        getLocationBtn.addEventListener('click', function () {
            if (navigator.geolocation) {
                getLocationBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Getting location...';
                getLocationBtn.disabled = true;

                navigator.geolocation.getCurrentPosition(
                    function (position) {
                        const latInput = document.getElementById('id_latitude');
                        const lngInput = document.getElementById('id_longitude');
                        if (latInput) latInput.value = position.coords.latitude.toFixed(6);
                        if (lngInput) lngInput.value = position.coords.longitude.toFixed(6);
                        getLocationBtn.innerHTML = '<i class="fas fa-check"></i> Location set!';
                        getLocationBtn.classList.add('btn-success');
                        setTimeout(() => {
                            getLocationBtn.innerHTML = '<i class="fas fa-location-crosshairs"></i> Use My Location';
                            getLocationBtn.disabled = false;
                            getLocationBtn.classList.remove('btn-success');
                        }, 2000);
                    },
                    function (error) {
                        getLocationBtn.innerHTML = '<i class="fas fa-times"></i> Failed to get location';
                        getLocationBtn.disabled = false;
                        setTimeout(() => {
                            getLocationBtn.innerHTML = '<i class="fas fa-location-crosshairs"></i> Use My Location';
                        }, 2000);
                    }
                );
            } else {
                alert('Geolocation is not supported by your browser.');
            }
        });
    }
});
