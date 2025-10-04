function openRestoreFacultyModal(facultyId) {
    const modal = document.getElementById(`restoreFacultyModal-${facultyId}`);
    
    // Move modal to body to ensure it's on top
    if (modal && modal.parentNode !== document.body) {
        document.body.appendChild(modal);
    }
    
    // Add body class to prevent scrolling
    document.body.style.overflow = 'hidden';
    
    modal.classList.remove('hidden');
    
    // Force reflow to ensure proper z-index
    modal.offsetHeight;
}

function closeRestoreFacultyModal(facultyId) {
    const modal = document.getElementById(`restoreFacultyModal-${facultyId}`);
    
    // Restore body scrolling
    document.body.style.overflow = '';
    
    modal.classList.add('hidden');
}

// Handle HTMX content swaps to reinitialize modals
document.addEventListener('htmx:afterSwap', function() {
    // Find all restore modals and ensure they're properly positioned
    const modals = document.querySelectorAll('[id^="restoreFacultyModal-"]');
    modals.forEach(modal => {
        if (modal.parentNode !== document.body) {
            document.body.appendChild(modal);
        }
    });
});