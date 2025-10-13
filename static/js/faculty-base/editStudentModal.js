// Student Edit Modal Functions
window.openEditModal = function(studentId) {
    const modal = document.getElementById(`editStudentModal-${studentId}`);
    if (modal) {
        modal.classList.remove('hidden');
        document.body.classList.add('overflow-hidden');
    }
};

window.closeEditModal = function(studentId) {
    const modal = document.getElementById(`editStudentModal-${studentId}`);
    if (modal) {
        modal.classList.add('hidden');
        document.body.classList.remove('overflow-hidden');
    }
};

// Student ID availability check for edit
async function checkStudentIdAvailabilityForEdit(studentId, originalId) {
    if (!studentId || studentId.length < 3) return;
    
    // If the ID hasn't changed, it's valid
    if (studentId === originalId) {
        const messageDiv = document.getElementById(`student-id-message-edit-${originalId}`);
        const inputField = document.querySelector(`#editStudentForm-${originalId} input[name="student_id"]`);
        
        inputField.classList.remove('border-red-500', 'focus:ring-red-500', 'border-gray-200');
        inputField.classList.add('border-green-500', 'focus:ring-green-500');
        messageDiv.className = 'text-green-500 text-sm mt-1';
        messageDiv.textContent = 'Current Student ID';
        messageDiv.classList.remove('hidden');
        return;
    }
    
    try {
        const response = await fetch('/Faculty/check-student-id/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector(`#editStudentForm-${originalId} [name=csrfmiddlewaretoken]`).value
            },
            body: JSON.stringify({student_id: studentId})
        });
        
        const data = await response.json();
        const inputField = document.querySelector(`#editStudentForm-${originalId} input[name="student_id"]`);
        const messageDiv = document.getElementById(`student-id-message-edit-${originalId}`);
        const submitBtn = document.getElementById(`submitEditBtn-${originalId}`);
        
        if (data.exists) {
            inputField.classList.add('border-red-500', 'focus:ring-red-500');
            inputField.classList.remove('border-gray-200', 'border-green-500');
            messageDiv.className = 'text-red-500 text-sm mt-1';
            messageDiv.textContent = 'This Student ID is already taken.';
            messageDiv.classList.remove('hidden');
            submitBtn.disabled = true;
        } else {
            inputField.classList.add('border-green-500', 'focus:ring-green-500');
            inputField.classList.remove('border-red-500', 'border-gray-200');
            messageDiv.className = 'text-green-500 text-sm mt-1';
            messageDiv.textContent = 'Student ID is available.';
            messageDiv.classList.remove('hidden');
            submitBtn.disabled = false;
        }
    } catch (error) {
        console.error('Error checking student ID:', error);
    }
}

// Initialize edit form handlers
document.addEventListener('DOMContentLoaded', function() {
    const editModals = document.querySelectorAll('[id^="editStudentModal-"]');
    
    editModals.forEach(modal => {
        const studentId = modal.id.split('-')[1];
        const form = document.getElementById(`editStudentForm-${studentId}`);
        
        if (form) {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                
                // Validate student ID
                const studentIdInput = this.querySelector('input[name="student_id"]');
                if (studentIdInput && studentIdInput.classList.contains('border-red-500')) {
                    alert('Please use a different Student ID. This one is already taken.');
                    return false;
                }
                
                // Submit form
                const formData = new FormData(this);
                const submitBtn = document.getElementById(`submitEditBtn-${studentId}`);
                
                if (submitBtn) {
                    submitBtn.disabled = true;
                    submitBtn.textContent = 'Saving...';
                }
                
                fetch(this.getAttribute('action'), {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                })
                .then(response => {
                    if (response.ok) {
                        window.location.reload();
                    } else {
                        throw new Error('Update failed');
                    }
                })
                .catch(error => {
                    console.error('Error updating student:', error);
                    alert('Error updating student. Please try again.');
                    if (submitBtn) {
                        submitBtn.disabled = false;
                        submitBtn.textContent = 'Save Changes';
                    }
                });
            });
        }
    });
});