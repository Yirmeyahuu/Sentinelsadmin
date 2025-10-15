function openDeadlineInfoModal(title, tier, date, time) {
    const modal = document.getElementById('deadlineInfoModal');
    const modalContent = modal.querySelector('.bg-white');
    const lateCompletionsList = document.getElementById('lateCompletionsList');
    
    // Set content
    document.getElementById('deadlineTitle').textContent = title;
    document.getElementById('deadlineDate').textContent = date;
    document.getElementById('deadlineTime').textContent = time;
    
    // Show loading state
    lateCompletionsList.innerHTML = `
        <div class="flex items-center justify-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-sky-600"></div>
        </div>
    `;
    
    // Fetch late completions data
    fetch(`/Faculty/get-late-completions/${encodeURIComponent(title)}/`)
        .then(response => response.json())
        .then(data => {
            if (data.late_completions && data.late_completions.length > 0) {
                lateCompletionsList.innerHTML = data.late_completions.map(completion => `
                    <div class="bg-rose-50 rounded-xl p-4 border border-rose-100">
                        <div class="flex items-center justify-between">
                            <div class="space-y-1">
                                <div class="flex items-center space-x-2">
                                    <h5 class="text-sm font-medium text-rose-900">${completion.student_name}</h5>
                                    <span class="text-xs text-rose-600">${completion.student_id}</span>
                                </div>
                                <p class="text-xs text-rose-600">Completed: ${completion.completed_at}</p>
                            </div>
                            <span class="text-sm font-medium text-rose-700">${completion.points} pts</span>
                        </div>
                    </div>
                `).join('');
            } else {
                // Show no submissions message
                lateCompletionsList.innerHTML = `
                    <div class="flex flex-col items-center justify-center py-8 bg-gray-50 rounded-2xl border-2 border-dashed border-gray-200">
                        <div class="p-3 bg-gray-100 rounded-xl mb-3">
                            <svg class="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" 
                                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                            </svg>
                        </div>
                        <p class="text-sm font-medium text-gray-500">
                            No student completed the task late
                        </p>
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            lateCompletionsList.innerHTML = `
                <div class="p-4 bg-rose-50 rounded-xl border border-rose-200">
                    <p class="text-sm text-rose-600 text-center">
                        Error loading late submissions. Please try again.
                    </p>
                </div>
            `;
        });
    
    // Set tier badge color and show modal
    const tierBadge = document.getElementById('deadlineTier');
    tierBadge.textContent = tier;
    tierBadge.className = getTierBadgeClass(tier);
    
    showModal(modal, modalContent);
    
    // Add event listener for clicking outside
    modal.addEventListener('click', e => {
        if (e.target === modal) closeDeadlineInfoModal();
    });
}

function getTierBadgeClass(tier) {
    switch(tier.toLowerCase()) {
        case 'novice':
            return 'px-4 py-1.5 rounded-full text-sm font-semibold bg-green-100 text-green-800';
        case 'junior':
            return 'px-4 py-1.5 rounded-full text-sm font-semibold bg-blue-100 text-blue-800';
        case 'senior':
            return 'px-4 py-1.5 rounded-full text-sm font-semibold bg-purple-100 text-purple-800';
        default:
            return 'px-4 py-1.5 rounded-full text-sm font-semibold bg-gray-100 text-gray-800';
    }
}

function showModal(modal, modalContent) {
    modal.classList.remove('opacity-0', 'pointer-events-none');
    modalContent.classList.remove('scale-95');
    modalContent.classList.add('scale-100');
}

function closeDeadlineInfoModal() {
    const modal = document.getElementById('deadlineInfoModal');
    const modalContent = modal.querySelector('.bg-white');
    
    modalContent.classList.remove('scale-100');
    modalContent.classList.add('scale-95');
    modal.classList.add('opacity-0', 'pointer-events-none');
}