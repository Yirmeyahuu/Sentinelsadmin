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