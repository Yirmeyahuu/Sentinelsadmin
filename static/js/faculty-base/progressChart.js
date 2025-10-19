// Initialize chart instance globally
let chartInstance;

window.initTierProgressChart = function() {
    // Get data from window object with validation
    const totalStudents = window.tierProgressData?.totalStudents || 0;
    const tierData = window.tierProgressData?.tierData || { novice: 0, junior: 0, senior: 0 };

    // Calculate completion rates and update UI
    function updateCompletionRates() {
        const cards = document.querySelectorAll('.tier-card');
        let maxCompletion = 0;
        let topTier = '';

        cards.forEach(card => {
            const count = parseInt(card.dataset.count);
            const completion = ((count / totalStudents) * 100).toFixed(1);
            
            // Update completion rate display
            const completionRateElem = card.querySelector('.completion-rate');
            if (completionRateElem) {
                completionRateElem.textContent = `${completion}%`;
            }
            const completionBarElem = card.querySelector('.completion-bar');
            if (completionBarElem) {
                completionBarElem.style.width = `${completion}%`;
            }

            // Track highest completion for top tier
            if (parseFloat(completion) > maxCompletion) {
                maxCompletion = parseFloat(completion);
                topTier = card.dataset.tier.charAt(0).toUpperCase() + card.dataset.tier.slice(1);
            }
        });

        // Update summary statistics safely
        const avgCompletionElem = document.getElementById('avgCompletion');
        if (avgCompletionElem) {
            avgCompletionElem.textContent = 
                ((Object.values(tierData).reduce((a, b) => a + b, 0) / (totalStudents * 3) * 100)).toFixed(1) + '%';
        }
        const topTierElem = document.getElementById('topTier');
        if (topTierElem) {
            topTierElem.textContent = topTier;
        }
    }

    // Destroy existing chart if it exists
    if (chartInstance) {
        chartInstance.destroy();
    }

    // Initialize Chart.js
    const ctxElem = document.getElementById('tierProgressChart');
    if (ctxElem) {
        const ctx = ctxElem.getContext('2d');
        
        // Calculate max value for better scaling
        const maxValue = Math.max(
            tierData.novice,
            tierData.junior,
            tierData.senior,
            totalStudents || 10
        );

            chartInstance = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Novice', 'Junior', 'Senior'],
                    datasets: [{
                        label: 'Students per Tier',
                        data: [tierData.novice, tierData.junior, tierData.senior],
                        backgroundColor: [
                            'rgba(14, 165, 233, 0.7)',  // sky-500
                            'rgba(6, 182, 212, 0.7)',   // cyan-500
                            'rgba(59, 130, 246, 0.7)'   // blue-500
                        ],
                        borderColor: [
                            'rgb(14, 165, 233)',  // sky-500
                            'rgb(6, 182, 212)',   // cyan-500
                            'rgb(59, 130, 246)'   // blue-500
                        ],
                        borderWidth: 0,
                        borderRadius: 16, // Rounded bars
                        barThickness: 280, // Thicker bars for modern look
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            backgroundColor: 'rgba(30, 41, 59, 0.95)', // slate-800
                            titleFont: { size: 16, weight: 'bold', family: "'Poppins', sans-serif" },
                            bodyFont: { size: 14, family: "'Poppins', sans-serif" },
                            padding: 14,
                            cornerRadius: 12,
                            displayColors: false,
                        },
                    },
                    layout: {
                        padding: { top: 24, right: 24, bottom: 24, left: 24 }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: Math.ceil(Math.max(maxValue, 5) / 5) * 5,
                            grid: { color: 'rgba(203, 213, 225, 0.1)' },
                            border: { display: false },
                            ticks: {
                                font: { size: 14, weight: 'bold', family: "'Poppins', sans-serif" },
                                color: '#64748b', // slate-500
                                stepSize: 1,
                                precision: 0,
                                padding: 8,
                            }
                        },
                        x: {
                            grid: { display: false },
                            border: { display: false },
                            ticks: {
                                font: { size: 15, weight: 'bold', family: "'Poppins', sans-serif" },
                                color: '#334155', // slate-800
                                padding: 12,
                            }
                        }
                    }
                }
            });
    }

    // View toggle handler
    const viewTypeSelect = document.getElementById('viewType');
    if (viewTypeSelect) {
        viewTypeSelect.addEventListener('change', function(e) {
            const cardsView = document.getElementById('cardsView');
            const chartView = document.getElementById('chartView');
            
            if (e.target.value === 'chart') {
                cardsView.classList.add('hidden');
                chartView.classList.remove('hidden');
                chartInstance.update();
            } else {
                cardsView.classList.remove('hidden');
                chartView.classList.add('hidden');
            }
        });
    }

    // Initialize completion rates
    updateCompletionRates();

    // Update "last updated" times
    setInterval(() => {
        document.querySelectorAll('.last-updated').forEach(el => {
            el.textContent = 'Updated just now';
        });
    }, 120000);
};

// Function to try initializing the chart
function tryInitTierProgressChart() {
    if (document.getElementById('tierProgressChart')) {
        console.log('Initializing Tier Progress Chart'); // Debug log
        // Add a small delay to ensure the script tag has been processed
        setTimeout(() => {
            window.initTierProgressChart && window.initTierProgressChart();
        }, 50);
    }
}

// Initialize on both DOMContentLoaded and HTMX afterSwap
document.addEventListener('DOMContentLoaded', tryInitTierProgressChart);
document.body.addEventListener('htmx:afterSwap', tryInitTierProgressChart);

//Time of update in Tier Cards
function updateTimestamps() {
    document.querySelectorAll('.last-updated').forEach(el => {
        const timestamp = new Date(el.dataset.timestamp);
        const now = new Date();
        const diffInMinutes = Math.floor((now - timestamp) / (1000 * 60));
        
        let timeAgo;
        if (diffInMinutes < 1) {
            timeAgo = 'just now';
        } else if (diffInMinutes < 60) {
            timeAgo = `${diffInMinutes}m ago`;
        } else if (diffInMinutes < 1440) {
            const hours = Math.floor(diffInMinutes / 60);
            timeAgo = `${hours}h ago`;
        } else {
            const days = Math.floor(diffInMinutes / 1440);
            timeAgo = `${days}d ago`;
        }
        
        el.textContent = `Updated ${timeAgo}`;
    });
}

// Update timestamps every minute
setInterval(updateTimestamps, 60000);

// Initial update
updateTimestamps();