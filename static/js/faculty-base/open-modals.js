
// Archive Modal
window.openArchiveModal = function() {
    document.getElementById('archiveModal').classList.remove('hidden');
};
window.closeArchiveModal = function() {
    document.getElementById('archiveModal').classList.add('hidden');
};

// Add Student Modal
window.openModal = function() {
    document.getElementById('modal').classList.remove('hidden');
};
window.closeModal = function() {
    document.getElementById('modal').classList.add('hidden');
};

// Edit Student Modal
window.openEditModal = function() {
    document.getElementById('editStudentModal').classList.remove('hidden');
};
window.closeEditModal = function() {
    document.getElementById('editStudentModal').classList.add('hidden');
};

// Move Student Modal
window.openMoveModal = function() {
    document.getElementById('moveModal').classList.remove('hidden');
};
window.closeMoveModal = function() {
    document.getElementById('moveModal').classList.add('hidden');
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

window.openFacultyActivityDeadlineModal = function(title, description) {
    document.getElementById('facultyActivityDeadlineTitle').textContent = title;
    document.getElementById('facultyActivityDeadlineDescription').textContent = description;
    document.getElementById('facultyActivityDeadlineModal').classList.remove('hidden');
    document.body.classList.add('overflow-hidden');
    const aside = document.querySelector('aside');
    if (aside) aside.classList.add('blur');
    // Store title for submission
    document.getElementById('facultyDeadlineForm').dataset.title = title;
};

window.closeFacultyActivityDeadlineModal = function() {
    document.getElementById('facultyActivityDeadlineModal').classList.add('hidden');
    document.body.classList.remove('overflow-hidden');
    const aside = document.querySelector('aside');
    if (aside) aside.classList.remove('blur');
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
    const date = document.getElementById('facultyDeadlineDate').value;
    const time24 = document.getElementById('facultyDeadlineTime').value; // "13:45"
    const time12 = convertTo12Hour(time24); // "01:45 PM"

    fetch('/Faculty/save-activity-deadline/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            title: title,
            date: date,
            time: time12 // Send as 12-hour format
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Deadline set!');
            closeFacultyActivityDeadlineModal();
        } else {
            alert('Failed to set deadline.');
        }
    });
};

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