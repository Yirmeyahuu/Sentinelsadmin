let editAssignmentCounters = {};
let editAssignments = {};

function addEditAssignment(facultyId) {
    if (!editAssignmentCounters[facultyId]) {
        editAssignmentCounters[facultyId] = document.querySelectorAll(`#editAssignmentsList-${facultyId} .assignment-item`).length;
    }
    
    const assignmentHtml = `
        <div class="assignment-item bg-gray-50 p-4 rounded-lg border" data-index="${editAssignmentCounters[facultyId]}">
            <div class="flex justify-between items-center mb-3">
                <h4 class="font-medium text-gray-700">Assignment ${editAssignmentCounters[facultyId] + 1}</h4>
                <button type="button" onclick="removeEditAssignment('${facultyId}', ${editAssignmentCounters[facultyId]})" 
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
            <input type="hidden" class="assignment-id" value="">
        </div>
    `;
    
    document.getElementById(`editAssignmentsList-${facultyId}`).insertAdjacentHTML('beforeend', assignmentHtml);
    editAssignmentCounters[facultyId]++;
    updateEditAssignmentsData(facultyId);
}

function removeEditAssignment(facultyId, index) {
    document.querySelector(`#editAssignmentsList-${facultyId} [data-index="${index}"]`).remove();
    updateEditAssignmentsData(facultyId);
}

function updateEditAssignmentsData(facultyId) {
    const assignmentItems = document.querySelectorAll(`#editAssignmentsList-${facultyId} .assignment-item`);
    editAssignments[facultyId] = [];
    
    assignmentItems.forEach(item => {
        const program = item.querySelector('.assignment-program').value;
        const yearSection = item.querySelector('.assignment-year-section').value;
        const semester = item.querySelector('.assignment-semester').value;
        const assignmentId = item.querySelector('.assignment-id').value;
        
        if (program && yearSection && semester) {
            const assignmentData = {
                program: program,
                year_section: yearSection,
                semester: semester
            };
            
            if (assignmentId) {
                assignmentData.id = assignmentId;
            }
            
            editAssignments[facultyId].push(assignmentData);
        }
    });
    
    document.getElementById(`editAssignmentsData-${facultyId}`).value = JSON.stringify(editAssignments[facultyId]);
}

// Add event listeners for edit assignment changes
document.addEventListener('change', function(e) {
    if (e.target.classList.contains('assignment-program') || 
        e.target.classList.contains('assignment-semester')) {
        const facultyId = e.target.closest('form').id.replace('editFacultyForm-', '');
        updateEditAssignmentsData(facultyId);
    }
});

document.addEventListener('input', function(e) {
    if (e.target.classList.contains('assignment-year-section')) {
        const facultyId = e.target.closest('form').id.replace('editFacultyForm-', '');
        updateEditAssignmentsData(facultyId);
    }
});

function openEditFacultyModal(facultyId) {
    document.getElementById(`editFacultyModal-${facultyId}`).classList.remove('hidden');
    // Initialize assignments data for this faculty
    updateEditAssignmentsData(facultyId);
}

function closeEditFacultyModal(facultyId) {
    document.getElementById(`editFacultyModal-${facultyId}`).classList.add('hidden');
}