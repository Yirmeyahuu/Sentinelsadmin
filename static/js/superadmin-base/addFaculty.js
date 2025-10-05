function formatFacultyName(input) {
    let value = input.value;
    // Remove any non-letter characters and convert to proper case
    value = value.replace(/[^a-zA-Z\s]/g, '');
    value = value.toLowerCase().replace(/\b\w/g, l => l.toUpperCase());
    input.value = value;
}

// Format middle initial (single letter + period)
function formatFacultyMiddleInitial(input) {
    let value = input.value.toUpperCase();
    // Remove any non-letter characters except period
    value = value.replace(/[^A-Z.]/g, '');
    
    // If there's a letter, ensure it has a period
    if (value.length > 0 && value.match(/[A-Z]/)) {
        // Get only the first letter and add period
        value = value.charAt(0) + '.';
    }
    
    input.value = value;
}

// Format year and section (1 digit + 1 letter)
function formatFacultyYearSection(input) {
    let value = input.value.toUpperCase();
    // Remove any characters that are not digits or letters
    value = value.replace(/[^0-9A-Z]/g, '');
    
    // Ensure format: first character is a digit (1-4), second is a letter
    if (value.length > 0) {
        let formatted = '';
        
        // First character should be a digit 1-4
        if (value.charAt(0).match(/[1-4]/)) {
            formatted += value.charAt(0);
        }
        
        // Second character should be a letter
        if (value.length > 1 && value.charAt(1).match(/[A-Z]/)) {
            formatted += value.charAt(1);
        }
        
        value = formatted;
    }
    
    input.value = value;
}

async function checkFacultyIdAvailability(facultyId) {
    if (!facultyId || facultyId.length < 3) return; // Don't check if too short
    
    try {
        const response = await fetch('/Superadmin/check-faculty-id/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({faculty_id: facultyId})
        });
        
        const data = await response.json();
        const inputField = document.querySelector('input[name="faculty_id"]');
        const messageDiv = document.getElementById('faculty-id-message') || createFacultyMessageDiv();
        
        if (data.exists) {
            inputField.classList.add('border-red-500', 'focus:ring-red-500');
            inputField.classList.remove('border-gray-200', 'focus:ring-blue-200');
            messageDiv.className = 'text-red-500 text-sm mt-1';
            messageDiv.textContent = 'This Faculty ID is already taken.';
        } else {
            inputField.classList.add('border-green-500', 'focus:ring-green-500');
            inputField.classList.remove('border-red-500', 'focus:ring-red-500', 'border-gray-200');
            messageDiv.className = 'text-green-500 text-sm mt-1';
            messageDiv.textContent = 'Faculty ID is available.';
        }
    } catch (error) {
        console.error('Error checking faculty ID:', error);
    }
}

function createFacultyMessageDiv() {
    const messageDiv = document.getElementById('faculty-id-message');
    messageDiv.classList.remove('hidden');
    return messageDiv;
}


let assignmentCounter = 0;
let assignments = [];

function addAssignment() {
    const assignmentHtml = `
        <div class="assignment-item bg-gray-50 p-4 rounded-lg border" data-index="${assignmentCounter}">
            <div class="flex justify-between items-center mb-3">
                <h4 class="font-medium text-gray-700">Assignment ${assignmentCounter + 1}</h4>
                <button type="button" onclick="removeAssignment(${assignmentCounter})" 
                        class="text-red-600 hover:text-red-800 transition-colors">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                    </svg>
                </button>
            </div>
            <div class="grid grid-cols-3 gap-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Program</label>
                    <select class="assignment-program w-full px-3 py-2 border border-gray-300 rounded-lg focus:border-blue-500 focus:ring-1 focus:ring-blue-500" required>
                        <option value="">Select Program</option>
                        <option value="Computer Science">Computer Science</option>
                        <option value="Information Technology">Information Technology</option>
                    </select>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Year & Section</label>
                    <input type="text" class="assignment-year-section w-full px-3 py-2 border border-gray-300 rounded-lg focus:border-blue-500 focus:ring-1 focus:ring-blue-500 uppercase text-center" 
                           placeholder="3A" maxlength="2" required oninput="formatFacultyYearSection(this)">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Semester</label>
                    <select class="assignment-semester w-full px-3 py-2 border border-gray-300 rounded-lg focus:border-blue-500 focus:ring-1 focus:ring-blue-500" required>
                        <option value="">Select Semester</option>
                        <option value="1st Semester">1st Semester</option>
                        <option value="2nd Semester">2nd Semester</option>
                        <option value="Summer">Summer</option>
                    </select>
                </div>
            </div>
        </div>
    `;
    
    document.getElementById('assignmentsList').insertAdjacentHTML('beforeend', assignmentHtml);
    assignmentCounter++;
    updateAssignmentsData();
}

// ... rest of your existing code remains the same

function removeAssignment(index) {
    document.querySelector(`[data-index="${index}"]`).remove();
    updateAssignmentsData();
}

function updateAssignmentsData() {
    const assignmentItems = document.querySelectorAll('#assignmentsList .assignment-item'); // More specific selector
    assignments = [];
    
    console.log('=== JAVASCRIPT DEBUG ===');
    console.log(`Found ${assignmentItems.length} assignment items`);
    
    assignmentItems.forEach((item, index) => {
        const program = item.querySelector('.assignment-program').value;
        const yearSection = item.querySelector('.assignment-year-section').value;
        const semester = item.querySelector('.assignment-semester').value;
        
        console.log(`Assignment ${index + 1}:`, { program, yearSection, semester });
        
        if (program && yearSection && semester) {
            assignments.push({
                program: program,
                year_section: yearSection,
                semester: semester
            });
        }
    });
    
    console.log('Final assignments array:', assignments);
    console.log('JSON string:', JSON.stringify(assignments));
    
    document.getElementById('assignmentsData').value = JSON.stringify(assignments);
}

// Add event listeners for assignment changes
document.addEventListener('change', function(e) {
    if (e.target.classList.contains('assignment-program') || 
        e.target.classList.contains('assignment-semester')) {
        updateAssignmentsData();
    }
});

document.addEventListener('input', function(e) {
    if (e.target.classList.contains('assignment-year-section')) {
        updateAssignmentsData();
    }
});

// Initialize with one assignment
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('addFacultyModal')) {
        addAssignment();
    }
});

// Modal functions
function openAddFacultyModal() {
    document.getElementById('addFacultyModal').classList.remove('hidden');
    // Reset form and assignments
    document.getElementById('facultyForm').reset();
    document.getElementById('assignmentsList').innerHTML = '';
    assignmentCounter = 0;
    assignments = [];
    
    // Clear validation messages and reset input styling
    const facultyIdInput = document.querySelector('input[name="faculty_id"]');
    const messageDiv = document.getElementById('faculty-id-message');
    if (facultyIdInput) {
        facultyIdInput.classList.remove('border-red-500', 'focus:ring-red-500', 'border-green-500', 'focus:ring-green-500');
        facultyIdInput.classList.add('border-gray-200', 'focus:ring-blue-200');
    }
    if (messageDiv) {
        messageDiv.classList.add('hidden');
        messageDiv.textContent = '';
    }
    
    addAssignment(); // Add initial assignment
    
    console.log('=== MODAL OPENED ===');
    console.log('Modal opened, assignments reset');
}

function closeAddFacultyModal() {
    document.getElementById('addFacultyModal').classList.add('hidden');
    // Reset form and assignments
    document.getElementById('facultyForm').reset();
    document.getElementById('assignmentsList').innerHTML = '';
    assignmentCounter = 0;
    assignments = [];
    
    console.log('=== MODAL CLOSED ===');
    console.log('Modal closed, assignments cleared');
}

// Add form submission debugging
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('facultyForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            console.log('=== FORM SUBMISSION ===');
            updateAssignmentsData(); // Ensure data is up to date
            console.log('Submitting assignments:', assignments);
            console.log('Hidden field value:', document.getElementById('assignmentsData').value);
            
            // Don't prevent default - let form submit normally
        });
    }
});