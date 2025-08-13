// Logout Modal
window.openLogoutModal = function() {
    document.getElementById("logoutModal").classList.remove("hidden");
    document.body.classList.add("overflow-hidden");
};

window.closeLogoutModal = function() {
    document.getElementById("logoutModal").classList.add("hidden");
    document.body.classList.remove("overflow-hidden");

};

window.logoutUser = function() {
    document.getElementById("logoutForm").submit();
};

// Archive Modal
window.openArchiveModal = function() {
    document.getElementById("archiveModal").classList.remove("hidden");
    document.body.classList.add("overflow-hidden");
};

window.closeArchiveModal = function() {
    document.getElementById("archiveModal").classList.add("hidden");
    document.body.classList.remove("overflow-hidden");
};

// Faculty Modal Functions
window.openEditFacultyModal = function(facultyId) {
    const modal = document.getElementById(`editFacultyModal-${facultyId}`);
    if (modal) {
        modal.classList.remove('hidden');
        document.body.classList.add('overflow-hidden');
    }
};

window.closeEditFacultyModal = function(facultyId) {
    const modal = document.getElementById(`editFacultyModal-${facultyId}`);
    if (modal) {
        modal.classList.add('hidden');
        document.body.classList.remove('overflow-hidden');
    }
};

// Close modal when clicking outside
document.addEventListener('click', function(event) {
    if (event.target.classList.contains('fixed')) {
        const facultyId = event.target.id.replace('editFacultyModal-', '');
        closeEditFacultyModal(facultyId);
    }
});

// Move Faculty Modal
window.openMoveFacultyModal = function(facultyId) {
    document.getElementById("move-faculty-id").value = facultyId; // <-- Set the hidden input!
    document.getElementById("moveFacultyModal").classList.remove("hidden");
    document.body.classList.add("overflow-hidden");
};

window.closeMoveFacultyModal = function() {
    document.getElementById("moveFacultyModal").classList.add("hidden");
    document.body.classList.remove("overflow-hidden");
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

// Add Faculty Modal
window.openAddFacultyModal = function() {
    document.getElementById("addFacultyModal").classList.remove("hidden");
    document.body.classList.add("overflow-hidden");

};

window.closeAddFacultyModal = function() {
    document.getElementById("addFacultyModal").classList.add("hidden");
    document.body.classList.remove("overflow-hidden");
};


// AJAX for Activate/Deactivate
window.activateGameTrigger = function() {
    updateGameTriggerLock(false); // isLock = False (unlocked/active)
};
window.deactivateGameTrigger = function() {
    updateGameTriggerLock(true); // isLock = True (locked/inactive)
};

function updateGameTriggerLock(isLock) {
    const tier = document.getElementById('setGameTriggerTier').value;
    const task = document.getElementById('setGameTriggerTask').value;
    fetch('/Superadmin/update-game-trigger/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            tier: tier,
            task: task,
            isLock: isLock
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Game trigger updated!');
            closeSetGameTriggerModal();
            // Reload the activity list content via HTMX
            htmx.ajax('GET', '/Superadmin/Activity-list/', '#mainContent');
        }
        else {
            alert('Failed to update game trigger.');
        }
    });
}

// Helper to get CSRF token of activity
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

window.setTierLock = function(tier, isLock) {
    fetch('/Superadmin/update-tier-lock/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            tier: tier,
            isLock: isLock
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Animate cards for this tier
            document.querySelectorAll(`[data-tier="${tier}"]`).forEach(card => {
                if (isLock) {
                    card.classList.add('bg-gray-700/70');
                    if (!card.querySelector('.lock-overlay')) {
                        const overlay = document.createElement('div');
                        overlay.className = "lock-overlay absolute inset-0 bg-gray-700/70 bg-opacity-60 flex items-center justify-center z-10 pointer-events-none transition-all duration-300";
                        overlay.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" class="w-16 h-16 text-gray-200 opacity-90" viewBox="0 0 24 24"><path fill="currentColor" d="M17 9V7c0-2.8-2.2-5-5-5S7 4.2 7 7v2c-1.7 0-3 1.3-3 3v7c0 1.7 1.3 3 3 3h10c1.7 0 3-1.3 3-3v-7c0-1.7-1.3-3-3-3zM9 7c0-1.7 1.3-3 3-3s3 1.3 3 3v2H9V7zm4 10c0 .6-.4 1-1 1s-1-.4-1-1v-3c0-.6.4-1 1-1s1 .4 1 1v3z"/></svg>`;
                        card.appendChild(overlay);
                    }
                    const img = card.querySelector('img');
                    if (img) img.classList.add('brightness-50');
                    const content = card.querySelector('.p-4');
                    if (content) content.classList.add('opacity-80');
                } else {
                    card.classList.remove('bg-gray-700/70');
                    const overlay = card.querySelector('.lock-overlay');
                    if (overlay) overlay.remove();
                    const img = card.querySelector('img');
                    if (img) img.classList.remove('brightness-50');
                    const content = card.querySelector('.p-4');
                    if (content) content.classList.remove('opacity-80');
                }
            });
        } else {
            alert('Failed to update tier lock.');
        }
    });
};


window.openActivityDetails = function(title, description) {
    document.getElementById('activityDetailsTitle').textContent = title;
    document.getElementById('activityDetailsDescription').textContent = description;
    document.getElementById('ActivityDetails').classList.remove('hidden');
    document.body.classList.add('overflow-hidden');
};

window.closeActivityDetails = function() {
    document.getElementById('ActivityDetails').classList.add('hidden');
    document.body.classList.remove('overflow-hidden');
};