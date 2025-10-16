// Floating "About Us" Button
window.initFacultyAboutUsButton = function() {
    // Remove existing button if any
    const existingBtn = document.getElementById('facultyAboutUsFloatBtn');
    if (existingBtn) {
        existingBtn.remove();
    }

    // Create button element
    const btn = document.createElement('div');
    btn.id = 'facultyAboutUsFloatBtn';
    btn.className = 'fixed bottom-20 right-6 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-full shadow-lg cursor-pointer transition-all duration-300 hover:scale-105 z-50';
    btn.innerHTML = `
        <div class="flex items-center space-x-2 group">
            <svg class="w-4 h-4 transition-transform group-hover:scale-110" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 2a8 8 0 100 16 8 8 0 000-16zm1 12H9v-2h2v2zm0-4H9V7h2v3z" clip-rule="evenodd" />
            </svg>
            <span class="text-sm font-medium">About Us</span>
        </div>
    `;

    // Redirect on click
    btn.addEventListener('click', function() {
        window.location.href = '/Faculty/Developers/';
    });

    // Append to body
    document.body.appendChild(btn);
};

// Auto-initialize About Us button when page loads
document.addEventListener('DOMContentLoaded', function() {
    window.initFacultyAboutUsButton();
});

// Reinitialize after HTMX swaps (if needed)
document.addEventListener('htmx:afterSwap', function() {
    setTimeout(() => {
        window.initFacultyAboutUsButton();
    }, 100);
});
