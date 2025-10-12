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