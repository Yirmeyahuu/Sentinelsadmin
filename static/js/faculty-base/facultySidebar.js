
document.addEventListener("DOMContentLoaded", function() {
    function setActiveSidebar() {
        // Remove highlights from all sidebar links
        document.querySelectorAll('aside [data-page]').forEach(link => {
            link.classList.remove('bg-white', 'text-blue-500');
        });

        // Highlight the current sub-link
        const current = document.querySelector('aside [data-page="' + window.location.pathname + '"]');
        if (current) {
            current.classList.add('bg-white', 'text-blue-500');
        }

        // Highlight the Student parent menu if any sub-link is active
        const studentPages = [
            "/Faculty/Student-progress/",
            "/Faculty/Student-list/",
            "/Faculty/Verify-students/",
            "/Faculty/Student-status/",
        ];
        const studentParent = document.querySelector('aside .students-parent-menu');
        if (studentParent) {
            if (studentPages.includes(window.location.pathname)) {
                studentParent.classList.add('bg-white', 'text-blue-500');
            } else {
                studentParent.classList.remove('bg-white', 'text-blue-500');
            }
        }
    }

    setActiveSidebar();
    document.body.addEventListener('htmx:pushedIntoHistory', setActiveSidebar);
});