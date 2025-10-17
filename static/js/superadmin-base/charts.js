window.initSuperadminHomeChart = function() {
    const chartElem = document.getElementById('programLineChart');
    if (!chartElem) return;

    // Use dynamic data from Django with fallback
    const allLabels = window.tierLabels || ["Novice", "Junior", "Senior"];
    const csData = window.csTierData || [0, 0, 0];
    const itData = window.itTierData || [0, 0, 0];

    console.log('Superadmin Chart Data:', { allLabels, csData, itData }); // Debug log

    // Destroy previous chart instance if exists
    if (window.superadminChartInstance) {
        window.superadminChartInstance.destroy();
    }

    // Calculate max value for better scaling
    const maxValue = Math.max(
        Math.max(...csData),
        Math.max(...itData)
    );

    const ctx = chartElem.getContext('2d');
    window.superadminChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: allLabels,
            datasets: [
                {
                    label: 'Computer Science',
                    data: csData,
                    borderColor: '#0ea5e9',
                    backgroundColor: 'rgba(14, 165, 233, 0.15)',
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: '#0ea5e9',
                    pointBorderColor: '#fff',
                    pointRadius: 6,
                    pointHoverRadius: 8,
                },
                {
                    label: 'Information Technology',
                    data: itData,
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.15)',
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: '#ef4444',
                    pointBorderColor: '#fff',
                    pointRadius: 6,
                    pointHoverRadius: 8,
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                    labels: { color: '#3b82f6' }
                }
            },
            scales: {
                x: {
                    ticks: { color: '#3b82f6', font: { size: 14, weight: 'bold' } },
                    grid: { 
                        color: '#3b82f6',
                        lineWidth: 1
                    }
                },
                y: {
                    beginAtZero: true,
                    title: { display: true, text: 'Students Completed', color: '#3b82f6', font: { size: 14, weight: 'bold' } },
                    min: 0,
                    max: window.totalStudentCount || Math.max(maxValue + 5, 10),
                    ticks: {
                        color: '#3b82f6',
                        stepSize: 1,
                        precision: 0,
                        callback: function(value) {
                            return Number.isInteger(value) ? value : null;
                        }
                    },
                    grid: { 
                        color: '#3b82f6',
                        lineWidth: 1
                    }
                }
            }
        }
    });

    // Dropdown menu logic
    const btn = document.getElementById('programMenuBtn');
    const menu = document.getElementById('programMenu');
    if (btn && menu) {
        btn.onclick = function(e) {
            e.stopPropagation();
            menu.classList.toggle('hidden');
        };
        document.addEventListener('click', function() {
            menu.classList.add('hidden');
        });
    }

    // Store current data in the chart instance for dropdown functionality
    window.superadminChartInstance.originalData = {
        labels: allLabels,
        csData: csData,
        itData: itData
    };

    window.changeProgram = function(program) {
        const data = window.superadminChartInstance.originalData;
        
        document.getElementById('programLabel').textContent = program === 'All' ? 'All Programs' : program;
        document.getElementById('programMenuBtnText').textContent = program === 'All' ? 'All Programs' : program;

        if (program === 'All') {
            window.superadminChartInstance.data = {
                labels: data.labels,
                datasets: [
                    {
                        label: 'Computer Science',
                        data: data.csData,
                        borderColor: '#0ea5e9',
                        backgroundColor: 'rgba(14, 165, 233, 0.15)',
                        tension: 0.4,
                        fill: true,
                        pointBackgroundColor: '#0ea5e9',
                        pointBorderColor: '#fff',
                        pointRadius: 6,
                        pointHoverRadius: 8,
                    },
                    {
                        label: 'Information Technology',
                        data: data.itData,
                        borderColor: '#6366F1',
                        backgroundColor: 'rgba(99, 102, 241, 0.15)',
                        tension: 0.4,
                        fill: true,
                        pointBackgroundColor: '#6366F1',
                        pointBorderColor: '#fff',
                        pointRadius: 6,
                        pointHoverRadius: 8,
                    }
                ]
            };
        } else if (program === 'Computer Science') {
            window.superadminChartInstance.data = {
                labels: data.labels,
                datasets: [
                    {
                        label: 'Computer Science',
                        data: data.csData,
                        borderColor: '#0ea5e9',
                        backgroundColor: 'rgba(14, 165, 233, 0.15)',
                        tension: 0.4,
                        fill: true,
                        pointBackgroundColor: '#0ea5e9',
                        pointBorderColor: '#fff',
                        pointRadius: 8,
                        pointHoverRadius: 10,
                    }
                ]
            };
        } else if (program === 'Information Technology') {
            window.superadminChartInstance.data = {
                labels: data.labels,
                datasets: [
                    {
                        label: 'Information Technology',
                        data: data.itData,
                        borderColor: '#6366F1',
                        backgroundColor: 'rgba(99, 102, 241, 0.15)',
                        tension: 0.4,
                        fill: true,
                        pointBackgroundColor: '#6366F1',
                        pointBorderColor: '#fff',
                        pointRadius: 8,
                        pointHoverRadius: 10,
                    }
                ]
            };
        }
        window.superadminChartInstance.update();
        menu.classList.add('hidden');
    };
    
    // Set default program
    window.changeProgram('All');
};

// Display chart on page load and after HTMX swaps
function tryInitSuperadminHomeChart() {
    if (document.getElementById('programLineChart')) {
        console.log('Initializing Superadmin Home Chart'); // Debug log
        // Add a small delay to ensure the script tag has been processed
        setTimeout(() => {
            window.initSuperadminHomeChart && window.initSuperadminHomeChart();
        }, 50);
    }
}

// Initialize on full page load
document.addEventListener('DOMContentLoaded', tryInitSuperadminHomeChart);

// Re-initialize after HTMX swaps
document.body.addEventListener('htmx:afterSwap', tryInitSuperadminHomeChart);