function hideHelpIfDevelopers() {
    const isDevPage = window.location.pathname.includes('/Superadmin/Developers/');
    const helpTooltip = document.getElementById('helpTooltip');
    if (helpTooltip) helpTooltip.style.display = isDevPage ? 'none' : '';

    // Hide/show "Need help?" button by text
    document.querySelectorAll('button, a').forEach(el => {
        if (el.textContent && el.textContent.trim().toLowerCase().includes('need help')) {
            el.style.display = isDevPage ? 'none' : '';
        }
    });

    // About Us button logic
    const aboutUsBtn = document.getElementById('superadminAboutUsFloatBtn');
    if (aboutUsBtn) {
        // Always show on non-Developers pages
        if (!isDevPage) aboutUsBtn.style.display = '';
        // Hide on Developers page
        else aboutUsBtn.style.display = 'none';
    }
}

// Hide About Us button when clicked (but only until next swap or navigation)
document.addEventListener('DOMContentLoaded', function() {
    const aboutUsBtn = document.getElementById('superadminAboutUsFloatBtn');
    if (aboutUsBtn) {
        aboutUsBtn.addEventListener('click', function() {
            aboutUsBtn.style.display = 'none';
        });
    }
    hideHelpIfDevelopers();
});

document.addEventListener('DOMContentLoaded', hideHelpIfDevelopers);
document.addEventListener('htmx:afterSwap', hideHelpIfDevelopers);

// Also observe DOM changes for dynamically added tooltips/buttons
const observer = new MutationObserver(hideHelpIfDevelopers);
observer.observe(document.body, { childList: true, subtree: true });