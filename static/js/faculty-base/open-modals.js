// Modal open/close utility functions

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

