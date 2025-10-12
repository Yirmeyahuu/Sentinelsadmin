//ARCHIVING FACULTY

// Archive Modal
window.openArchiveModal = function() {
    document.getElementById("archiveModal").classList.remove("hidden");
    document.body.classList.add("overflow-hidden");
};

window.closeArchiveModal = function() {
    document.getElementById("archiveModal").classList.add("hidden");
    document.body.classList.remove("overflow-hidden");
};