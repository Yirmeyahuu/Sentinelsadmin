function toggleTemplateDropdown() {
    const dropdown = document.getElementById('templateDropdown');
    dropdown.classList.toggle('hidden');
}

// New export dropdown function
function toggleExportDropdown() {
    const dropdown = document.getElementById('exportDropdown');
    dropdown.classList.toggle('hidden');
}

// Enhanced click outside handler for both dropdowns
document.addEventListener('click', function(e) {
    // Template dropdown
    const templateDropdown = document.getElementById('templateDropdown');
    const templateButton = e.target.closest('[onclick="toggleTemplateDropdown()"]');
    
    if (!templateButton && !templateDropdown.contains(e.target)) {
        templateDropdown.classList.add('hidden');
    }
    
    // Export dropdown
    const exportDropdown = document.getElementById('exportDropdown');
    const exportButton = e.target.closest('[onclick="toggleExportDropdown()"]');
    
    if (!exportButton && !exportDropdown.contains(e.target)) {
        exportDropdown.classList.add('hidden');
    }
});

function openImportCsvModal() {
    const modal = document.getElementById('importCsvModal');
    const modalContent = document.getElementById('importModalContent');
    
    modal.classList.remove('hidden');
    
    // Animate modal appearance
    setTimeout(() => {
        modalContent.classList.remove('scale-95', 'opacity-0');
        modalContent.classList.add('scale-100', 'opacity-100');
    }, 10);
}

function closeImportCsvModal() {
    const modal = document.getElementById('importCsvModal');
    const modalContent = document.getElementById('importModalContent');
    
    // Animate modal disappearance
    modalContent.classList.remove('scale-100', 'opacity-100');
    modalContent.classList.add('scale-95', 'opacity-0');
    
    setTimeout(() => {
        modal.classList.add('hidden');
        // Reset form and file info
        document.getElementById('csv_file').value = '';
        document.getElementById('selectedFileInfo').classList.add('hidden');
    }, 300);
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
            fileInfo.classList.add('hidden');
            return;
        }
        
        // Validate file size (max 10MB)
        const maxSize = 10 * 1024 * 1024; // 10MB
        if (file.size > maxSize) {
            alert('File size should not exceed 10MB.');
            input.value = '';
            fileInfo.classList.add('hidden');
            return;
        }
        
        // Display file information
        fileName.textContent = file.name;
        fileSize.textContent = `${(file.size / 1024 / 1024).toFixed(2)} MB`;
        fileInfo.classList.remove('hidden');
    } else {
        fileInfo.classList.add('hidden');
    }
}

// Close modal when clicking outside
document.getElementById('importCsvModal').addEventListener('click', function(e) {
    if (e.target === this) {
        closeImportCsvModal();
    }
});

// Drag and drop functionality
const dropZone = document.getElementById('dropZone');

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
        document.getElementById('csv_file').files = files;
        handleFileSelect(document.getElementById('csv_file'));
    }
}