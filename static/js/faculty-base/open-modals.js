
// Archive Modal
window.openArchiveModal = function() {
    document.getElementById('archiveModal').classList.remove('hidden');
};
window.closeArchiveModal = function() {
    document.getElementById('archiveModal').classList.add('hidden');
};

// Add Student Modal
window.openStudentModal = function() {
    document.getElementById('modal').classList.remove('hidden');
};
window.closeStudentModal = function() {
    document.getElementById('modal').classList.add('hidden');
};


// Student Modal Functions
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


// Move Student Modal
window.openMoveStudentModal = function(studentId) {
    document.getElementById("move-student-id").value = studentId;
    document.getElementById("moveStudentModal").classList.remove("hidden");
    document.body.classList.add("overflow-hidden");
};

window.closeMoveStudentModal = function() {
    document.getElementById("moveStudentModal").classList.add("hidden");
    document.body.classList.remove("overflow-hidden");
};

// Progress Modal
window.openProgressModal = function() {
    document.getElementById('progressModal').classList.remove('hidden');
};
window.closeProgressModal = function() {
    document.getElementById('progressModal').classList.add('hidden');
};

// Notification Modal
window.openNotificationModal = function() {
    document.getElementById('notificationModal').classList.remove('hidden');
};
window.closeNotificationModal = function() {
    document.getElementById('notificationModal').classList.add('hidden');
};

// Logout Modal
window.openLogoutModal = function() {
    document.getElementById('logoutModal').classList.remove('hidden');
};
window.closeLogoutModal = function() {
    document.getElementById('logoutModal').classList.add('hidden');
};


// Set Faculty Activity Deadline Modal
window.facultyTierLockedAlert = function(event) {
    event.stopPropagation();
    alert("Tier is locked. Contact Super Administrator.");
};

window.openFacultyActivityDeadlineModal = function(title, description, tier) {
    document.getElementById('facultyActivityDeadlineTitle').textContent = title;
    document.getElementById('facultyActivityDeadlineDescription').textContent = description;
    document.getElementById('facultyActivityDeadlineModal').classList.remove('hidden');
    document.body.classList.add('overflow-hidden');
    // Store title and tier for submission
    const form = document.getElementById('facultyDeadlineForm');
    form.dataset.title = title;
    form.dataset.tier = tier;
};

window.closeFacultyActivityDeadlineModal = function() {
    document.getElementById('facultyActivityDeadlineModal').classList.add('hidden');
    document.body.classList.remove('overflow-hidden');
    // Reset form
    document.getElementById('facultyDeadlineForm').reset();
};

function convertTo12Hour(time24) {
    if (!time24) return "";
    const [hour, minute] = time24.split(':');
    let h = parseInt(hour, 10);
    const ampm = h >= 12 ? 'PM' : 'AM';
    h = h % 12;
    if (h === 0) h = 12;
    return `${h.toString().padStart(2, '0')}:${minute} ${ampm}`;
}

// Example usage in your submit function:
window.submitFacultyDeadline = function(event) {
    event.preventDefault();
    const form = document.getElementById('facultyDeadlineForm');
    const title = form.dataset.title;
    const tier = form.dataset.tier;
    const date = document.getElementById('facultyDeadlineDate').value;
    const time24 = document.getElementById('facultyDeadlineTime').value;
    const time12 = convertTo12Hour(time24);

    fetch('/Faculty/save-activity-deadline/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            title: title,
            tier: tier,
            date: date,
            time: time12
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Deadline set!');
            closeFacultyActivityDeadlineModal();
            location.reload(); // Reload to update calendar
        } else {
            alert('Failed to set deadline.');
        }
    });
};


window.removeActivityDeadline = function(title) {
    if (confirm(`Are you sure you want to remove the deadline for "${title}"?`)) {
        const formData = new FormData();
        formData.append('title', title);
        formData.append('csrfmiddlewaretoken', getCookie('csrftoken'));

        fetch('/Faculty/remove-deadline/', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.ok) {
                alert('Deadline removed successfully!');
                location.reload(); // Reload to update the UI
            } else {
                alert('Failed to remove deadline.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while removing the deadline.');
        });
    }
};

// Helper function to get CSRF token (if not already present)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Helper to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {    
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

window.openEditProfileModal = function() {
    document.getElementById('editProfileModal').classList.remove('hidden');
};

window.closeEditProfileModal = function() {
    document.getElementById('editProfileModal').classList.add('hidden');
};