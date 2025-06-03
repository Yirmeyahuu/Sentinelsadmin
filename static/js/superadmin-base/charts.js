window.initSuperadminHomeChart = function() {
    const chartElem = document.getElementById('programLineChart');
    if (!chartElem) return;

    const allLabels = ["Novice", "Junior", "Senior"];
    const csData = [12, 8, 5]; // Replace with your dynamic data if needed
    const itData = [10, 7, 9]; // Replace with your dynamic data if needed

    // Destroy previous chart instance if exists
    if (window.superadminChartInstance) {
        window.superadminChartInstance.destroy();
    }

    const ctx = chartElem.getContext('2d');
    window.superadminChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: allLabels,
            datasets: [
                {
                    label: 'Computer Science',
                    data: csData,
                    borderColor: '#f59e42',
                    backgroundColor: 'rgba(245, 158, 66, 0.15)',
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: '#f59e42',
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
                    labels: { color: '#fff' }
                }
            },
            scales: {
                x: {
                    ticks: { color: '#fff' },
                    grid: { color: 'rgba(255,255,255,0.2)' }
                },
                y: {
                    beginAtZero: true,
                    title: { display: true, text: 'Students', color: '#fff' },
                    ticks: { color: '#fff' },
                    grid: { color: 'rgba(255,255,255,0.2)' }
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

    window.changeProgram = function(program) {
        document.getElementById('programLabel').textContent = program === 'All' ? 'All Programs' : program;
        document.getElementById('programMenuBtnText').textContent = program === 'All' ? 'All Programs' : program;

        if (program === 'All') {
            window.superadminChartInstance.data = {
                labels: allLabels,
                datasets: [
                    {
                        label: 'Computer Science',
                        data: csData,
                        borderColor: '#f59e42',
                        backgroundColor: 'rgba(245, 158, 66, 0.15)',
                        tension: 0.4,
                        fill: true,
                        pointBackgroundColor: '#f59e42',
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
            };
        } else if (program === 'Computer Science') {
            window.superadminChartInstance.data = {
                labels: allLabels,
                datasets: [
                    {
                        label: 'Computer Science',
                        data: csData,
                        borderColor: '#f59e42',
                        backgroundColor: 'rgba(245, 158, 66, 0.15)',
                        tension: 0.4,
                        fill: true,
                        pointBackgroundColor: '#f59e42',
                        pointBorderColor: '#fff',
                        pointRadius: 8,
                        pointHoverRadius: 10,
                    }
                ]
            };
        } else if (program === 'Information Technology') {
            window.superadminChartInstance.data = {
                labels: allLabels,
                datasets: [
                    {
                        label: 'Information Technology',
                        data: itData,
                        borderColor: '#ef4444',
                        backgroundColor: 'rgba(239, 68, 68, 0.15)',
                        tension: 0.4,
                        fill: true,
                        pointBackgroundColor: '#ef4444',
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

// Initialize on full page load
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('programLineChart')) {
        window.initSuperadminHomeChart();
    }
});

// Re-initialize after HTMX swaps
document.body.addEventListener('htmx:afterSwap', function() {
    if (document.getElementById('programLineChart')) {
        window.initSuperadminHomeChart();
    }
});