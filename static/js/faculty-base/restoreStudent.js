function openRestoreStudentModal(studentId) {
    document.getElementById('restoreStudentId').value = studentId;
    document.getElementById('restoreStudentModal').classList.remove('hidden');
}
function closeRestoreStudentModal() {
    document.getElementById('restoreStudentModal').classList.add('hidden');
}