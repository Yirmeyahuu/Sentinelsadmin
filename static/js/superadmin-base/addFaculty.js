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
                    <input type="text" class="assignment-year-section w-full px-3 py-2 border border-gray-300 rounded-lg focus:border-blue-500 focus:ring-1 focus:ring-blue-500" 
                           placeholder="e.g. 3A" required>
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