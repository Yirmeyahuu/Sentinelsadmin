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