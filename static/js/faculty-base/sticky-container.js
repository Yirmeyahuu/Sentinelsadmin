// Function to show/hide sticky container based on current page
function updateStickyContainer() {
    const container = document.getElementById('stickyContainer');
    const isHomePage = window.location.pathname === '/Faculty/homepage/';
    
    if (container) {
        if (isHomePage) {
            container.style.display = 'block';
        } else {
            container.style.display = 'none';
        }
    }
}

// Update on initial page load
document.addEventListener('DOMContentLoaded', updateStickyContainer);

// Update on HTMX before swap
document.body.addEventListener('htmx:beforeSwap', function(evt) {
    const isHomePage = evt.detail.pathInfo.requestPath === '/Faculty/homepage/';
    const container = document.getElementById('stickyContainer');
    
    if (container) {
        container.style.display = isHomePage ? 'block' : 'none';
    }
});

// Handle browser back/forward
window.addEventListener('popstate', updateStickyContainer);