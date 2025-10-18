window.confirmDeadlineRemoval = function(event, title) {
    event.stopPropagation();
    activityToRemove = title;
    
    // Update modal content
    document.getElementById('activityTitle').textContent = title;
    
    // Show modal
    document.getElementById('removeDeadlineModal').classList.remove('hidden');
    document.body.classList.add('overflow-hidden');
};

window.closeDeadlineModal = function() {
    document.getElementById('removeDeadlineModal').classList.add('hidden');
    document.body.classList.remove('overflow-hidden');
    activityToRemove = null;
};

window.executeDeadlineRemoval = function() {
    if (!activityToRemove) return;
    
    fetch('/Faculty/remove-deadline/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            title: activityToRemove
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert(data.message);
            closeDeadlineModal();
            location.reload();
        } else {
            alert(data.message || 'Failed to remove deadline.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while removing the deadline.');
    });
};


// Close modal when clicking outside
document.addEventListener('click', (e) => {
    const modal = document.getElementById('removeDeadlineModal');
    if (e.target === modal) {
        closeDeadlineModal();
    }
});

// Close modal with ESC key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeDeadlineModal();
    }
});