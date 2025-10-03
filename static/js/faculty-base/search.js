/**
 * student Search Functionality
 * Handles search operations, clear functionality, and UI enhancements
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeSearch();
});

function initializeSearch() {
    const searchInput = document.querySelector('input[name="search"]');
    const searchForm = document.querySelector('form[method="get"]');
    const searchContainer = document.querySelector('.group');
    
    if (!searchInput || !searchForm) return;

    // Auto-submit on Enter key
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            this.form.submit();
        }
    });

    // Focus animations
    searchInput.addEventListener('focus', function() {
        searchContainer.classList.add('ring-4', 'ring-blue-100');
    });

    searchInput.addEventListener('blur', function() {
        searchContainer.classList.remove('ring-4', 'ring-blue-100');
    });

    // Real-time search (optional - for instant filtering)
    searchInput.addEventListener('input', debounce(function() {
        if (this.value.length >= 2) {
            performLiveSearch(this.value);
        } else if (this.value.length === 0) {
            clearLiveSearch();
        }
    }, 300));

    // Initialize search button functionality
    initializeSearchButton();
}

/**
 * Clear search functionality
 */
function clearSearch() {
    const searchInput = document.querySelector('input[name="search"]');
    if (searchInput) {
        searchInput.value = '';
        searchInput.form.submit();
    }
}

/**
 * Initialize search button with enhanced feedback
 */
function initializeSearchButton() {
    const searchButton = document.querySelector('button[type="submit"]');
    const searchForm = document.querySelector('form[method="get"]');
    
    if (!searchButton || !searchForm) return;

    searchButton.addEventListener('click', function(e) {
        e.preventDefault();
        
        // Add loading state
        showSearchLoading();
        
        // Submit form after brief delay for visual feedback
        setTimeout(() => {
            searchForm.submit();
        }, 150);
    });
}

/**
 * Show loading state on search button
 */
function showSearchLoading() {
    const searchButton = document.querySelector('button[type="submit"]');
    if (!searchButton) return;

    const originalContent = searchButton.innerHTML;
    
    // Show loading spinner
    searchButton.innerHTML = `
        <svg class="animate-spin w-3.5 h-3.5" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
    `;
    
    searchButton.disabled = true;
}

/**
 * Perform live search (optional feature)
 */
function performLiveSearch(query) {
    const studentRows = document.querySelectorAll('.studentRow');
    let visibleCount = 0;
    
    studentRows.forEach(row => {
        const rowText = row.textContent.toLowerCase();
        const searchQuery = query.toLowerCase();
        
        if (rowText.includes(searchQuery)) {
            row.style.display = '';
            visibleCount++;
        } else {
            row.style.display = 'none';
        }
    });
    
    // Update live counter if exists
    updateLiveCounter(visibleCount, query);
}

/**
 * Clear live search results
 */
function clearLiveSearch() {
    const studentRows = document.querySelectorAll('.studentRow');
    studentRows.forEach(row => {
        row.style.display = '';
    });
    
    // Remove live counter
    const liveCounter = document.querySelector('.live-search-counter');
    if (liveCounter) {
        liveCounter.remove();
    }
}

/**
 * Update live search counter
 */
function updateLiveCounter(count, query) {
    let counter = document.querySelector('.live-search-counter');
    
    if (!counter) {
        counter = document.createElement('div');
        counter.className = 'live-search-counter absolute top-full left-0 mt-2 px-3 py-1 bg-green-50 text-green-700 text-xs font-medium rounded-lg border border-green-200 z-10';
        
        const searchContainer = document.querySelector('.group');
        if (searchContainer) {
            searchContainer.appendChild(counter);
        }
    }
    
    counter.textContent = `${count} result${count !== 1 ? 's' : ''} found for "${query}"`;
}

/**
 * Debounce function to limit API calls
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Advanced search filters (can be extended)
 */
function initializeAdvancedFilters() {
    // Program filter
    const programFilter = document.querySelector('#program-filter');
    if (programFilter) {
        programFilter.addEventListener('change', function() {
            applyFilters();
        });
    }
    
    // Status filter
    const statusFilter = document.querySelector('#status-filter');
    if (statusFilter) {
        statusFilter.addEventListener('change', function() {
            applyFilters();
        });
    }
}

/**
 * Apply multiple filters
 */
function applyFilters() {
    const searchQuery = document.querySelector('input[name="search"]').value.toLowerCase();
    const programFilter = document.querySelector('#program-filter')?.value || '';
    const statusFilter = document.querySelector('#status-filter')?.value || '';
    
    const studentRows = document.querySelectorAll('.studentRow');
    let visibleCount = 0;
    
    studentRows.forEach(row => {
        const cells = row.querySelectorAll('td');
        if (cells.length < 6) return;
        
        const fullName = cells[1].textContent.toLowerCase();
        const studentId = cells[0].textContent.toLowerCase();
        const program = cells[2].textContent;
        const status = cells[5].textContent.trim();
        
        // Check search query
        const matchesSearch = !searchQuery || 
            fullName.includes(searchQuery) || 
            studentId.includes(searchQuery) || 
            program.toLowerCase().includes(searchQuery);
        
        // Check program filter
        const matchesProgram = !programFilter || program === programFilter;
        
        // Check status filter
        const matchesStatus = !statusFilter || status === statusFilter;
        
        if (matchesSearch && matchesProgram && matchesStatus) {
            row.style.display = '';
            visibleCount++;
        } else {
            row.style.display = 'none';
        }
    });
    
    updateLiveCounter(visibleCount, searchQuery || 'filtered results');
}

/**
 * Highlight search terms in results
 */
function highlightSearchTerms(query) {
    if (!query) return;
    
    const studentRows = document.querySelectorAll('.studentRow');
    const regex = new RegExp(`(${query})`, 'gi');
    
    studentRows.forEach(row => {
        const cells = row.querySelectorAll('td');
        cells.forEach(cell => {
            if (cell.textContent.toLowerCase().includes(query.toLowerCase())) {
                cell.innerHTML = cell.textContent.replace(regex, '<mark class="bg-yellow-200 px-1 rounded">$1</mark>');
            }
        });
    });
}

/**
 * Export search results functionality
 */
function exportSearchResults() {
    const visibleRows = document.querySelectorAll('.studentRow:not([style*="display: none"])');
    const data = [];
    
    visibleRows.forEach(row => {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 6) {
            data.push({
                student_id: cells[0].textContent.trim(),
                full_name: cells[1].textContent.trim(),
                program: cells[2].textContent.trim(),
                year_section: cells[3].textContent.trim(),
                semester: cells[4].textContent.trim(),
                status: cells[5].textContent.trim()
            });
        }
    });
    
    // Convert to CSV and download
    downloadCSV(data, 'student_search_results.csv');
}

/**
 * Download data as CSV
 */
function downloadCSV(data, filename) {
    if (data.length === 0) return;
    
    const headers = Object.keys(data[0]);
    const csvContent = [
        headers.join(','),
        ...data.map(row => headers.map(header => `"${row[header]}"`).join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
}

// Initialize advanced features if needed
document.addEventListener('DOMContentLoaded', function() {

     initializeAdvancedFilters();

     const searchQuery = document.querySelector('input[name="search"]').value;
     if (searchQuery) {
         highlightSearchTerms(searchQuery);
     }
});