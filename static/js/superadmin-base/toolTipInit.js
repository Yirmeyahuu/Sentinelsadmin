//Tool Tip Initialization

// Initialize tooltip when page loads
document.addEventListener('DOMContentLoaded', function() {
    if (window.initTooltip) {
        window.initTooltip();
    }
});

// Reinitialize tooltip after HTMX content swaps
document.addEventListener('htmx:afterSwap', function() {
    if (window.initTooltip) {
        window.initTooltip();
    }
});