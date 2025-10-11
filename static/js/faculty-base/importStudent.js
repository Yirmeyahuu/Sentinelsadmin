// Dropdown toggle functions
function toggleExportDropdown() {
    const dropdown = document.getElementById('exportDropdown');
    dropdown.classList.toggle('hidden');
}

function toggleTemplateDropdown() {
    const dropdown = document.getElementById('templateDropdown');
    dropdown.classList.toggle('hidden');
}

// Enhanced click outside handler for both dropdowns
document.addEventListener('click', function(e) {
    // Template dropdown
    const templateDropdown = document.getElementById('templateDropdown');
    const templateButton = e.target.closest('[onclick="toggleTemplateDropdown()"]');
    
    if (!templateButton && templateDropdown && !templateDropdown.contains(e.target)) {
        templateDropdown.classList.add('hidden');
    }
    
    // Export dropdown
    const exportDropdown = document.getElementById('exportDropdown');
    const exportButton = e.target.closest('[onclick="toggleExportDropdown()"]');
    
    if (!exportButton && exportDropdown && !exportDropdown.contains(e.target)) {
        exportDropdown.classList.add('hidden');
    }
});

// Enhanced import modal functions
function openImportCsvModal() {
    const modal = document.getElementById('importCsvModal');
    const modalContent = modal.querySelector('.relative');
    
    // Reset form before opening
    resetImportForm();
    
    modal.classList.remove('hidden');
    
    // Animate modal appearance
    setTimeout(() => {
        if (modalContent) {
            modalContent.classList.remove('scale-95', 'opacity-0');
            modalContent.classList.add('scale-100', 'opacity-100');
        }
    }, 10);
}

function closeImportCsvModal() {
    const modal = document.getElementById('importCsvModal');
    const modalContent = modal.querySelector('.relative');
    
    // Animate modal disappearance
    if (modalContent) {
        modalContent.classList.remove('scale-100', 'opacity-100');
        modalContent.classList.add('scale-95', 'opacity-0');
    }
    
    setTimeout(() => {
        modal.classList.add('hidden');
        // Reset form and file info
        resetImportForm();
    }, 300);
}

// New function to reset import form
function resetImportForm() {
    const form = document.querySelector('#importCsvModal form');
    const fileInput = document.querySelector('input[name="csv_file"]');
    const fileInfo = document.getElementById('selectedFileInfo');
    const submitButton = document.querySelector('#importCsvModal button[type="submit"]');
    
    // Reset form
    if (form) {
        form.reset();
    }
    
    // Clear file input properly
    if (fileInput) {
        fileInput.value = '';
        // Create a new file input to completely reset the files property
        const newFileInput = fileInput.cloneNode(true);
        fileInput.parentNode.replaceChild(newFileInput, fileInput);
        
        // Re-attach event listeners to the new input
        newFileInput.addEventListener('change', function() {
            handleFileSelect(this);
        });
    }
    
    // Hide file info
    if (fileInfo) {
        fileInfo.classList.add('hidden');
    }
    
    // Reset submit button
    if (submitButton) {
        submitButton.disabled = false;
        submitButton.innerHTML = `
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
            </svg>
            <span>Import Students</span>
        `;
    }
}

// Enhanced file selection handler
function handleFileSelect(input) {
    const file = input.files[0];
    const fileInfo = document.getElementById('selectedFileInfo');
    const fileName = document.getElementById('selectedFileName');
    const fileSize = document.getElementById('selectedFileSize');
    
    if (file) {
        const extension = file.name.split('.').pop().toLowerCase();
        
        // Validate file type
        if (!['csv', 'xlsx', 'xls'].includes(extension)) {
            alert('Please select a CSV or Excel file (.csv, .xlsx, .xls).');
            input.value = '';
            if (fileInfo) fileInfo.classList.add('hidden');
            return;
        }
        
        // Validate file size (max 10MB)
        const maxSize = 10 * 1024 * 1024; // 10MB
        if (file.size > maxSize) {
            alert('File size should not exceed 10MB.');
            input.value = '';
            if (fileInfo) fileInfo.classList.add('hidden');
            return;
        }
        
        // Display file information if elements exist
        if (fileName) fileName.textContent = file.name;
        if (fileSize) fileSize.textContent = `${(file.size / 1024 / 1024).toFixed(2)} MB`;
        if (fileInfo) fileInfo.classList.remove('hidden');
    } else {
        if (fileInfo) fileInfo.classList.add('hidden');
    }
}

// Close modal when clicking outside
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('importCsvModal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                closeImportCsvModal();
            }
        });
    }
});

// Enhanced drag and drop functionality
document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('dropZone');
    
    if (dropZone) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, unhighlight, false);
        });

        function highlight(e) {
            dropZone.classList.add('border-blue-500', 'bg-blue-50');
        }

        function unhighlight(e) {
            dropZone.classList.remove('border-blue-500', 'bg-blue-50');
        }

        dropZone.addEventListener('drop', handleDrop, false);

        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            if (files.length > 0) {
                const fileInput = document.querySelector('input[name="csv_file"]');
                if (fileInput) {
                    fileInput.files = files;
                    handleFileSelect(fileInput);
                }
            }
        }
    }
});

// Form validation before submission with better reset handling
document.addEventListener('DOMContentLoaded', function() {
    // Use event delegation to handle dynamically created forms
    document.addEventListener('submit', function(e) {
        // Check if this is the import form
        if (e.target.closest('#importCsvModal form')) {
            const form = e.target;
            const fileInput = form.querySelector('input[name="csv_file"]');
            
            if (!fileInput || !fileInput.files || !fileInput.files.length) {
                e.preventDefault();
                alert('Please select a file to import.');
                return false;
            }
            
            // Show loading state
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.innerHTML = `
                    <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span>Importing...</span>
                `;
                submitButton.disabled = true;
            }
            
            // Don't auto-close modal - let the server response handle it
            return true;
        }
    });
});

// Listen for page changes to reset modal state
document.addEventListener('DOMContentLoaded', function() {
    // Reset modal when page loads/reloads
    const modal = document.getElementById('importCsvModal');
    if (modal && !modal.classList.contains('hidden')) {
        closeImportCsvModal();
    }
});

// Handle page visibility changes
document.addEventListener('visibilitychange', function() {
    if (!document.hidden) {
        // Page became visible again, reset modal if needed
        const modal = document.getElementById('importCsvModal');
        if (modal && !modal.classList.contains('hidden')) {
            resetImportForm();
        }
    }
});