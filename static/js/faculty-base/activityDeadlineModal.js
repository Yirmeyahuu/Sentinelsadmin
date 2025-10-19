// Set Faculty Activity Deadline Modal
window.facultyTierLockedAlert = function(event) {
    event.stopPropagation();
    alert("Tier is locked. Contact Super Administrator.");
};

window.openFacultyActivityDeadlineModal = function(title, description, tier) {
    console.log('Opening modal with:', { title, description, tier });
    document.getElementById('facultyActivityDeadlineTitle').textContent = title;
    document.getElementById('facultyActivityDeadlineDescription').textContent = description;
    document.getElementById('facultyActivityDeadlineModal').classList.remove('hidden');
    document.body.classList.add('overflow-hidden');
    // Store title and tier for submission
    const form = document.getElementById('facultyDeadlineForm');
    form.dataset.title = title;
    form.dataset.tier = tier;
    console.log('Form dataset set:', form.dataset);
};

window.closeFacultyActivityDeadlineModal = function() {
    document.getElementById('facultyActivityDeadlineModal').classList.add('hidden');
    document.body.classList.remove('overflow-hidden');
    // Reset form
    document.getElementById('facultyDeadlineForm').reset();
};

function showLoadingOnCard(title) {
    // Find the specific card using the data-title attribute
    const card = document.querySelector(`[data-title="${title.replace(/"/g, '\\"')}"]`);
    if (card) {
        // Create the overlay div
        const overlay = document.createElement('div');
        overlay.className = 'absolute inset-0 bg-gray-900/70 backdrop-blur-sm flex items-center justify-center z-10';
        
        // Create the SVG spinner using Tailwind classes
        overlay.innerHTML = `
            <svg class="animate-spin h-8 w-8 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
        `;
        
        // Append the overlay to the card
        card.appendChild(overlay);
    }
}

function convertTo12Hour(time24) {
    if (!time24) return "";
    const [hour, minute] = time24.split(':');
    let h = parseInt(hour, 10);
    const ampm = h >= 12 ? 'PM' : 'AM';
    h = h % 12;
    if (h === 0) h = 12;
    const result = `${h.toString().padStart(2, '0')}:${minute} ${ampm}`;
    console.log('Time conversion:', time24, '->', result);
    return result;
}

// Submit deadline with better error handling
window.submitFacultyDeadline = function(event) {
    event.preventDefault();
    console.log('=== SUBMIT FACULTY DEADLINE ===');
    
    const form = document.getElementById('facultyDeadlineForm');
    const title = form.dataset.title;
    const tier = form.dataset.tier;
    const date = document.getElementById('facultyDeadlineDate').value;
    const time24 = document.getElementById('facultyDeadlineTime').value;
    const time12 = convertTo12Hour(time24);

    // Show loading on card BEFORE closing modal
    showLoadingOnCard(title);
    closeFacultyActivityDeadlineModal();

    const payload = {
        title: title,
        tier: tier,
        date: date,
        time: time12
    };
    
    console.log('Payload to send:', payload);
    console.log('Payload as JSON:', JSON.stringify(payload));
    
    const csrfToken = getCookie('csrftoken');
    console.log('CSRF Token:', csrfToken ? 'Found' : 'NOT FOUND');

    fetch('/Faculty/save-activity-deadline/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(payload)
    })
    .then(response => {
        console.log('Response received');
        console.log('Response status:', response.status);
        console.log('Response ok:', response.ok);
        console.log('Response headers:', [...response.headers.entries()]);
        
        // Clone the response so we can read it twice if needed
        return response.clone().text().then(text => {
            console.log('Raw response text:', text);
            try {
                const json = JSON.parse(text);
                console.log('Parsed JSON:', json);
                return json;
            } catch (e) {
                console.error('Failed to parse JSON:', e);
                console.error('Text that failed to parse:', text);
                throw new Error('Invalid JSON response: ' + text);
            }
        });
    })
    .then(data => {
        if (data.status === 'success') {
            // Wait a short moment to show the loading animation
            setTimeout(() => {
                location.reload();
            }, 600); // 600ms delay for animation visibility
        } else {
            alert('Error: ' + data.message); // Show alert only on error
        }
    })
    .catch(error => {
        console.error('=== FETCH ERROR ===');
        console.error('Error type:', error.name);
        console.error('Error message:', error.message);
        console.error('Error stack:', error.stack);
        alert('An error occurred while setting the deadline: ' + error.message);
    })
    .finally(() => {
        console.log('=== END SUBMIT ===');
    });
};

// Global variable to store activity title for removal
let activityToRemove = null;

window.confirmDeadlineRemoval = function(event, title) {
    event.stopPropagation();
    activityToRemove = title;
    console.log('Confirming removal for:', title);
    
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
    if (!activityToRemove) {
        console.error('No activity to remove');
        return;
    }
    
    const title = activityToRemove;

    // Close modal and show loading spinner on the card
    closeDeadlineModal();
    showLoadingOnCard(title);

    console.log('=== REMOVE DEADLINE ===');
    console.log('Removing deadline for:', title);
    
    const csrfToken = getCookie('csrftoken');
    console.log('CSRF Token:', csrfToken ? 'Found' : 'NOT FOUND');
    
    fetch('/Faculty/remove-deadline/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            title: title
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            closeDeadlineModal();
            location.reload(); // Reload the page instead of showing an alert
        } else {
            alert('Error: ' + data.message); // Show alert only on error
        }
    })
    .catch(error => {
        console.error('Error removing deadline:', error);
        alert('An error occurred while removing the deadline.');
    });
};

// Helper to get CSRF token
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