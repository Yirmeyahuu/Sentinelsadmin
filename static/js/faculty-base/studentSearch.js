document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('studentSearch');
    if (!searchInput) return;

    let debounceTimeout;

    searchInput.addEventListener('input', function(e) {
        clearTimeout(debounceTimeout);
        debounceTimeout = setTimeout(() => {
            const searchValue = e.target.value.toLowerCase();
            
            // Get all student rows
            const studentRows = document.querySelectorAll('tbody tr');
            
            studentRows.forEach(row => {
                const studentId = row.querySelector('td:nth-child(2)').textContent.toLowerCase();
                const studentName = row.querySelector('td:nth-child(1)').textContent.toLowerCase();
                
                // Check if the search value matches student ID or name
                const matches = studentId.includes(searchValue) || 
                              studentName.includes(searchValue);
                
                // Show/hide rows based on match
                row.style.display = matches ? '' : 'none';
                
                // Add/remove highlight class
                if (matches && searchValue) {
                    row.classList.add('bg-sky-50');
                    row.classList.remove('hover:bg-sky-50');
                } else {
                    row.classList.remove('bg-sky-50');
                    row.classList.add('hover:bg-sky-50');
                }
            });
        }, 300); // Debounce delay
    });

    // Handle form submission for server-side search
    searchInput.closest('form')?.addEventListener('submit', function(e) {
        e.preventDefault();
        const searchValue = searchInput.value.trim();
        if (searchValue) {
            const currentUrl = new URL(window.location.href);
            currentUrl.searchParams.set('search', searchValue);
            window.location.href = currentUrl.toString();
        }
    });
});