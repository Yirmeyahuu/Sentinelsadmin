function hideHelpIfDevelopers() {
    const isDevPage = window.location.pathname.includes('/Faculty/Developers/');
    const isFacultyProfilePage = window.location.pathname.includes('/Faculty/account/');
    const shouldHide = isDevPage || isFacultyProfilePage;
    const helpTooltip = document.getElementById('helpTooltip');
    if (helpTooltip) helpTooltip.style.display = shouldHide ? 'none' : '';

    // Hide/show "Need help?" button by text
    document.querySelectorAll('button, a').forEach(el => {
        if (el.textContent && el.textContent.trim().toLowerCase().includes('need help')) {
            el.style.display = shouldHide ? 'none' : '';
        }
    });

    // About Us button logic
    const aboutUsBtn = document.getElementById('facultyAboutUsFloatBtn');
    if (aboutUsBtn) {
        // Always show on other pages
        if (!shouldHide) aboutUsBtn.style.display = '';
        // Hide on Developers or Faculty Profile page
        else aboutUsBtn.style.display = 'none';
    }
}


// Hide About Us button when clicked (but only until next swap or navigation)
document.addEventListener('DOMContentLoaded', function() {
    const aboutUsBtn = document.getElementById('facultyAboutUsFloatBtn');
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