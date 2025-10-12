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