// Logout Modal
window.openLogoutModal = function() {
    document.getElementById("logoutModal").classList.remove("hidden");
    document.body.classList.add("overflow-hidden");
    document.querySelector('aside').classList.add('blur');
};

window.closeLogoutModal = function() {
    document.getElementById("logoutModal").classList.add("hidden");
    document.body.classList.remove("overflow-hidden");
    document.querySelector('aside').classList.remove('blur');

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

// Edit Faculty Modal
window.openEditFacultyModal = function() {
    document.getElementById("editFacultyModal").classList.remove("hidden");
    document.body.classList.add("overflow-hidden");
    document.querySelector('aside').classList.add('blur');
};

window.closeEditFacultyModal = function() {
    document.getElementById("editFacultyModal").classList.add("hidden");
    document.body.classList.remove("overflow-hidden");
    document.querySelector('aside').classList.remove('blur');
};

// Move Faculty Modal
window.openMoveFacultyModal = function() {
    document.getElementById("moveFacultyModal").classList.remove("hidden");
    document.body.classList.add("overflow-hidden");
    document.querySelector('aside').classList.add('blur');
};

window.closeMoveFacultyModal = function() {
    document.getElementById("moveFacultyModal").classList.add("hidden");
    document.body.classList.remove("overflow-hidden");
    document.querySelector('aside').classList.remove('blur');
};

// Add Faculty Modal
window.openModal = function() {
    document.getElementById("modal").classList.remove("hidden");
    document.body.classList.add("overflow-hidden");
    document.querySelector('aside').classList.add('blur');
    
};

window.closeModal = function() {
    document.getElementById("modal").classList.add("hidden");
    document.body.classList.remove("overflow-hidden");
    document.querySelector('aside').classList.remove('blur');
};


// Set Game Trigger Modal
window.setGameTrigger = function(tier, title, description) {
    document.getElementById('setGameTriggerTier').value = tier;
    document.getElementById('setGameTriggerTask').value = title;
    document.getElementById('setGameTriggerTitle').value = title;
    document.getElementById('setGameTriggerDescription').value = description;
    document.getElementById('setGameTriggerModal').classList.remove('hidden');
    document.body.classList.add('overflow-hidden');
    const aside = document.querySelector('aside');
    if (aside) aside.classList.add('blur');
};

window.closeSetGameTriggerModal = function() {
    document.getElementById('setGameTriggerModal').classList.add('hidden');
    document.body.classList.remove('overflow-hidden');
    const aside = document.querySelector('aside');
    if (aside) aside.classList.remove('blur');
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