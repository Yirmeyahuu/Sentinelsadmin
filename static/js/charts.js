// Chart.js and Neon Glow Plugin integration for Faculty Home

window.initFacultyHomeChart = function() {
    const tierColors = {
        Novice: { neonColor: '#0ff', neonFill: 'rgba(0,255,255,0.15)' },
        Junior: { neonColor: '#ff00de', neonFill: 'rgba(255,0,222,0.15)' },
        Senior: { neonColor: '#fff700', neonFill: 'rgba(255,247,0,0.15)' }
    };
    const tierData = {
        Novice: { labels: ['Task 1', 'Task 2', 'Task 3', 'Boss Battle'], data: [15, 12, 10, 8] },
        Junior: { labels: ['Task 1', 'Task 2', 'Task 3', 'Boss Battle'], data: [10, 9, 7, 5] },
        Senior: { labels: ['Task 1', 'Task 2', 'Task 3', 'Boss Battle'], data: [7, 6, 4, 2] }
    };
    let currentTier = 'All';
    let chartInstance;

    // Dropdown menu logic
    const btn = document.getElementById('tierMenuBtn');
    const menu = document.getElementById('tierMenu');
    if (btn && menu) {
        btn.onclick = function(e) {
            e.stopPropagation();
            menu.classList.toggle('hidden');
        };
        document.addEventListener('click', function() {
            menu.classList.add('hidden');
        });
    }

    function getAllTierDatasets() {
        return [
            {
                label: 'Novice',
                data: tierData.Novice.data,
                borderColor: tierColors.Novice.neonColor,
                backgroundColor: tierColors.Novice.neonFill,
                tension: 0.4,
                fill: true,
                pointBackgroundColor: tierColors.Novice.neonColor,
                pointBorderColor: '#fff',
                pointRadius: 6,
                pointHoverRadius: 8,
            },
            {
                label: 'Junior',
                data: tierData.Junior.data,
                borderColor: tierColors.Junior.neonColor,
                backgroundColor: tierColors.Junior.neonFill,
                tension: 0.4,
                fill: true,
                pointBackgroundColor: tierColors.Junior.neonColor,
                pointBorderColor: '#fff',
                pointRadius: 6,
                pointHoverRadius: 8,
            },
            {
                label: 'Senior',
                data: tierData.Senior.data,
                borderColor: tierColors.Senior.neonColor,
                backgroundColor: tierColors.Senior.neonFill,
                tension: 0.4,
                fill: true,
                pointBackgroundColor: tierColors.Senior.neonColor,
                pointBorderColor: '#fff',
                pointRadius: 6,
                pointHoverRadius: 8,
            }
        ];
    }

    function changeTier(tier) {
        currentTier = tier;
        document.getElementById('tierLabel').textContent = tier === 'All' ? 'All Tier' : tier;
        document.getElementById('tierMenuBtnText').textContent = tier === 'All' ? 'All Tier' : tier;

        if (tier === 'All') {
            chartInstance.data.labels = tierData.Novice.labels;
            chartInstance.data.datasets = getAllTierDatasets();
            chartInstance.options.plugins.neonGlow.glowColor = undefined;
        } else {
            chartInstance.data.labels = tierData[tier].labels;
            chartInstance.data.datasets = [{
                label: 'Accomplished',
                data: tierData[tier].data,
                borderColor: tierColors[tier].neonColor,
                backgroundColor: tierColors[tier].neonFill,
                tension: 0.4,
                fill: true,
                pointBackgroundColor: tierColors[tier].neonColor,
                pointBorderColor: '#fff',
                pointRadius: 6,
                pointHoverRadius: 8,
            }];
            chartInstance.options.plugins.neonGlow.glowColor = tierColors[tier].neonColor;
        }
        chartInstance.update();
        menu.classList.add('hidden');
    }

    // Chart.js setup
    const ctxElem = document.getElementById('noviceLineChart');
    if (ctxElem) {
        const ctx = ctxElem.getContext('2d');
        if (window.facultyHomeChartInstance) {
            window.facultyHomeChartInstance.destroy();
        }
        chartInstance = window.facultyHomeChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: tierData.Novice.labels,
                datasets: getAllTierDatasets()
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: true,
                        labels: { color: '#fff' }
                    },
                    neonGlow: {
                        glowColor: undefined,
                        glowBlur: 20
                    }
                },
                scales: {
                    x: {
                        ticks: { color: '#fff' },
                        grid: { color: 'rgba(255,255,255,0.2)' }
                    },
                    y: {
                        beginAtZero: true,
                        title: { display: true, text: 'Students Accomplished', color: '#fff' },
                        ticks: { color: '#fff' },
                        grid: { color: 'rgba(255,255,255,0.2)' }
                    }
                }
            }
        });
        // Expose changeTier globally for button onclicks
        window.changeTier = changeTier;
        changeTier(currentTier);
    }
};

// Display chart on page load and after HTMX swaps
function tryInitFacultyHomeChart() {
    if (document.getElementById('noviceLineChart')) {
        window.initFacultyHomeChart && window.initFacultyHomeChart();
    }
}

document.addEventListener('DOMContentLoaded', tryInitFacultyHomeChart);
document.body.addEventListener('htmx:afterSwap', tryInitFacultyHomeChart);