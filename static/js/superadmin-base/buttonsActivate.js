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

window.toggleTierLock = function(tier) {
    const btn = document.getElementById(`tierLockBtn-${tier}`);
    const isLocked = btn.getAttribute('data-locked') === 'true';

    // Toggle the lock state
    const newLockState = !isLocked;

    fetch('/Superadmin/update-tier-lock/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            tier: tier,
            isLock: newLockState
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update button UI
            btn.setAttribute('data-locked', newLockState ? 'true' : 'false');
            if (newLockState) {
                btn.textContent = 'Activate';
                btn.className = 'bg-green-700 hover:bg-green-900 text-white px-6 py-2 rounded-xl text-sm transition-ease-in-out duration-200';
            } else {
                btn.textContent = 'Deactivate';
                btn.className = 'bg-red-700 hover:bg-red-900 text-white px-6 py-2 rounded-xl text-sm transition-ease-in-out duration-200';
            }
            location.reload();
        } else {
            alert('Failed to update tier lock.');
        }
    });
};