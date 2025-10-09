// Format student name (proper case)
function formatStudentName(input) {
    let value = input.value;
    value = value.replace(/[^a-zA-Z\s]/g, '');
    value = value.toLowerCase().replace(/\b\w/g, l => l.toUpperCase());
    input.value = value;
}

// Format middle initial (single letter + period)
function formatStudentMiddleInitial(input) {
    let value = input.value.toUpperCase();
    value = value.replace(/[^A-Z.]/g, '');
    
    if (value.length > 0 && value.match(/[A-Z]/)) {
        value = value.charAt(0) + '.';
    }
    
    input.value = value;
}

// Check student ID availability
async function checkStudentIdAvailability(studentId) {
    if (!studentId || studentId.length < 3) return;
    
    try {
        const response = await fetch('/Faculty/check-student-id/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('#studentForm [name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({student_id: studentId})
        });
        
        const data = await response.json();
        const inputField = document.querySelector('#studentForm input[name="student_id"]');
        const messageDiv = document.getElementById('student-id-message');
        
        if (data.exists) {
            inputField.classList.add('border-red-500', 'focus:ring-red-500');
            inputField.classList.remove('border-gray-200', 'focus:ring-blue-200', 'border-green-500');
            messageDiv.className = 'text-red-500 text-sm mt-1';
            messageDiv.textContent = 'This Student ID is already taken.';
            messageDiv.classList.remove('hidden');
        } else {
            inputField.classList.add('border-green-500', 'focus:ring-green-500');
            inputField.classList.remove('border-red-500', 'focus:ring-red-500', 'border-gray-200');
            messageDiv.className = 'text-green-500 text-sm mt-1';
            messageDiv.textContent = 'Student ID is available.';
            messageDiv.classList.remove('hidden');
        }
    } catch (error) {
        console.error('Error checking student ID:', error);
    }
}

// Modal functions
function openStudentModal() {
    const modal = document.getElementById('addStudentModal');
    const form = document.getElementById('studentForm');
    
    // Show modal
    modal.classList.remove('hidden');
    
    // Reset form completely
    form.reset();
    
    // Set the correct form action URL
    form.setAttribute('action', '/Faculty/add/');
    
    // Reset validation
    const studentIdInput = form.querySelector('input[name="student_id"]');
    const messageDiv = document.getElementById('student-id-message');
    
    if (studentIdInput) {
        studentIdInput.classList.remove('border-red-500', 'focus:ring-red-500', 'border-green-500', 'focus:ring-green-500');
        studentIdInput.classList.add('border-gray-200', 'focus:ring-blue-200');
    }
    
    if (messageDiv) {
        messageDiv.classList.add('hidden');
        messageDiv.textContent = '';
    }
    
    console.log('Student modal opened - form action:', form.getAttribute('action'));
}

function closeAddStudentModal() {
    const modal = document.getElementById('addStudentModal');
    const form = document.getElementById('studentForm');
    
    modal.classList.add('hidden');
    form.reset();
    
    console.log('Student modal closed');
}

// Remove the formListenerAdded flag completely and use a different approach
document.addEventListener('DOMContentLoaded', function() {
    const studentForm = document.getElementById('studentForm');
    
    if (studentForm) {
        // Remove any existing event listeners by cloning the form element
        const newForm = studentForm.cloneNode(true);
        studentForm.parentNode.replaceChild(newForm, studentForm);
        
        // Add fresh event listener to the new form
        newForm.addEventListener('submit', function(e) {
            e.preventDefault(); // Prevent default form submission
            
            console.log('Form submit event triggered');
            console.log('Form action:', this.getAttribute('action'));
            console.log('Form method:', this.getAttribute('method'));
            
            // Check if student ID is available
            const studentIdInput = this.querySelector('input[name="student_id"]');
            if (studentIdInput && studentIdInput.classList.contains('border-red-500')) {
                alert('Please use a different Student ID. This one is already taken.');
                return false;
            }
            
            // Check if faculty assignment is selected
            const assignmentSelect = this.querySelector('select[name="faculty_assignment_id"]');
            if (!assignmentSelect || !assignmentSelect.value) {
                alert('Please select a class assignment.');
                return false;
            }
            
            console.log('Form validation passed, submitting...');
            
            // Disable the submit button to prevent double submission
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.textContent = 'Adding...';
            }
            
            // Get form data
            const formData = new FormData(this);
            
            // Submit form via fetch
            fetch(this.getAttribute('action'), {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => {
                console.log('Response status:', response.status);
                if (response.redirected) {
                    // Django redirected us - follow the redirect
                    window.location.href = response.url;
                } else if (response.ok) {
                    // Success - reload the page
                    window.location.reload();
                } else {
                    throw new Error('Form submission failed');
                }
            })
            .catch(error => {
                console.error('Error submitting form:', error);
                alert('Error adding student. Please try again.');
                
                // Re-enable the submit button
                if (submitButton) {
                    submitButton.disabled = false;
                    submitButton.textContent = 'Add Student';
                }
            });
        });
    }
    
    // Clean URL on page load if it has ?search= with no value
    if (window.location.search === '?search=' || window.location.search === '?search') {
        window.history.replaceState({}, document.title, window.location.pathname);
    }
});