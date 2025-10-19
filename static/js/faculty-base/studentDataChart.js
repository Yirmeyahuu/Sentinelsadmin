function viewDetails(studentId) {
    const modal = document.getElementById('studentTaskDataModal');
    const modalContainer = modal.querySelector('.relative');
    
    if (!modal || !modalContainer) {
        console.error('Modal elements not found');
        return;
    }

    // Show modal with animation
    modal.classList.remove('hidden');
    setTimeout(() => {
        modalContainer.classList.remove('opacity-0', 'scale-95');
        modalContainer.classList.add('opacity-100', 'scale-100');
        
        // Fetch data after modal is visible
        fetchStudentTaskData(studentId, 'novice');
    }, 50);

    // Update modal content with a modern UI
    modalContainer.innerHTML = `
        <div class="bg-white rounded-2xl shadow-xl p-6 sm:p-8 w-full max-w-4xl mx-auto transform transition-all">
            <div class="flex items-start justify-between mb-6">
                <div>
                    <h2 class="text-2xl font-bold text-gray-800">Student Progress</h2>
                    <p class="text-sm text-gray-500">Task completion and points overview</p>
                </div>
                <button onclick="closeModal()" class="p-2 rounded-full text-gray-400 hover:bg-gray-100 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-400 transition-colors duration-200">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>

            <!-- Tier Filter -->
            <div class="mb-6">
                <div class="inline-flex rounded-lg shadow-sm bg-gray-100 p-1 space-x-1">
                    <button onclick="switchTier(this, 'novice')" class="tier-btn px-4 py-2 text-sm font-semibold rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-sky-500 bg-white text-sky-600 shadow">Novice</button>
                    <button onclick="switchTier(this, 'junior')" class="tier-btn px-4 py-2 text-sm font-semibold rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-sky-500 text-gray-600 hover:bg-gray-200">Junior</button>
                    <button onclick="switchTier(this, 'senior')" class="tier-btn px-4 py-2 text-sm font-semibold rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-sky-500 text-gray-600 hover:bg-gray-200">Senior</button>
                </div>
            </div>
            <div class="h-[450px] w-full">
                <canvas id="studentTaskChart"></canvas>
            </div>
        </div>
    `;

    // Store student ID for tier switching
    modalContainer.dataset.studentId = studentId;
}

async function fetchStudentTaskData(studentId, tier) {
    try {
        const response = await fetch(`/Faculty/student-data/modal/${studentId}/`);
        if (!response.ok) {
            throw new Error('Failed to fetch student data');
        }
        const data = await response.json();
        
        const tierData = (data.task_details && data.task_details[tier]) ? data.task_details[tier] : {};
        
        renderTaskChart(tierData, tier);
    } catch (error) {
        console.error("Error fetching student data:", error);
        renderTaskChart({}, tier);
    }
}

function renderTaskChart(taskData, tier) {
    const canvas = document.getElementById('studentTaskChart');
    if (!canvas) {
        console.error('Canvas element not found');
        return;
    }
    const ctx = canvas.getContext('2d');

    if (window.studentTaskChart && typeof window.studentTaskChart.destroy === 'function') {
        window.studentTaskChart.destroy();
    }
    
    canvas.width = canvas.parentElement.offsetWidth;
    canvas.height = canvas.parentElement.offsetHeight;

    const tasks = {
        novice: [
            "Novice_Task_1(Collect Books)", "Novice_Task_2(Collect USB)",
            "Novice_Task_3(QNA)", "Novice_Task_4_(Defeat Rootkit)"
        ],
        junior: [
            "Junior_Task_1(Collect Books)", "Junior_Task_2(Caesar's QNA)",
            "Junior_Task_3(Collect USB)", "Junior_Task_4(Bellaso's QNA)",
            "Junior_Task_5(QNA)", "Junior_Task_6(Defeat Serpentix2)"
        ],
        senior: [
            "Senior_Task_1(Collect Books)", "Senior_Task_2(QNA)",
            "Senior_Task_3(Collect USB)", "Senior_Task_4(QNA)",
            "Senior_Task_5(QNA)", "Senior_Task_6(Defeat Rootkit2)"
        ]
    };

    const taskMaxPoints = {
        // Novice
        "Novice_Task_1(Collect Books)": 250,
        "Novice_Task_2(Collect USB)": 250,
        "Novice_Task_3(QNA)": 550,
        "Novice_Task_4_(Defeat Rootkit)": 350,
        // Junior
        "Junior_Task_1(Collect Books)": 250,
        "Junior_Task_2(Caesar's QNA)": 350,
        "Junior_Task_3(Collect USB)": 250,
        "Junior_Task_4(Bellaso's QNA)": 350,
        "Junior_Task_5(QNA)": 550,
        "Junior_Task_6(Defeat Serpentix2)": 350,
        // Senior
        "Senior_Task_1(Collect Books)": 250,
        "Senior_Task_2(QNA)": 350,
        "Senior_Task_3(Collect USB)": 250,
        "Senior_Task_4(QNA)": 350,
        "Senior_Task_5(QNA)": 550,
        "Senior_Task_6(Defeat Rootkit2)": 550
    };

    taskData = taskData || {};

    const chartData = new Array(tasks[tier].length).fill(0);
    const labels = tasks[tier].map(taskName => taskName.split('(')[1].replace(')', ''));
    const completionDates = new Array(tasks[tier].length).fill(null);
    const maxPointsForTier = tasks[tier].map(taskName => taskMaxPoints[taskName] || 0);

    tasks[tier].forEach((taskName, index) => {
        if (taskData[taskName]) {
            chartData[index] = taskData[taskName].points || 0;
            completionDates[index] = taskData[taskName].completedAt;
        }
    });

    const taskColors = {
        'Collect Books': 'rgba(59, 130, 246, 0.8)',
        'Collect USB': 'rgba(16, 185, 129, 0.8)',
        'QNA': 'rgba(245, 158, 11, 0.8)',
        'Defeat Rootkit': 'rgba(239, 68, 68, 0.8)',
        'Caesar\'s QNA': 'rgba(168, 85, 247, 0.8)',
        'Bellaso\'s QNA': 'rgba(168, 85, 247, 0.8)',
        'Defeat Serpentix2': 'rgba(236, 72, 153, 0.8)',
        'Defeat Rootkit2': 'rgba(220, 38, 38, 0.8)'
    };

    const getTaskType = (label) => {
        for (const type of Object.keys(taskColors)) {
            if (label.includes(type)) return type;
        }
        return 'Other';
    };

    try {
        const yAxisMax = Math.max(...maxPointsForTier);

        window.studentTaskChart = new Chart(ctx, {
            type: 'bar',
            indexAxis: 'y', // Make the bar chart horizontal
            data: {
                labels: labels,
                datasets: [{
                    label: 'Points',
                    data: chartData,
                    backgroundColor: labels.map(label => taskColors[getTaskType(label)] || 'rgba(156, 163, 175, 0.8)'),
                    borderColor: labels.map(label => (taskColors[getTaskType(label)] || 'rgb(107, 114, 128)').replace('0.8', '1')),
                    borderWidth: 1,
                    borderRadius: 6,
                    barThickness: 60,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 600,
                    easing: 'easeInOutQuart'
                },
                plugins: {
                    legend: {
                        display: false // Hide legend for a cleaner look
                    },
                    tooltip: {
                        enabled: true,
                        backgroundColor: 'rgba(17, 24, 39, 0.95)',
                        titleFont: { size: 14, family: "'Poppins', sans-serif", weight: 'bold' },
                        bodyFont: { size: 13, family: "'Poppins', sans-serif" },
                        padding: 16,
                        cornerRadius: 8,
                        displayColors: false,
                        callbacks: {
                            title: (context) => `Task: ${context[0].label}`,
                            label: (context) => {
                                const index = context.dataIndex;
                                const completedAt = completionDates[index];
                                const maxPoints = maxPointsForTier[index];
                                return [
                                    `Points: ${context.raw} / ${maxPoints}`,
                                    completedAt ? `Completed: ${new Date(completedAt).toLocaleString()}` : 'Not completed'
                                ];
                            }
                        }
                    }
                },
                scales: {
                    x: { // Value axis
                        beginAtZero: true,
                        min: 0,
                        max: yAxisMax > 0 ? Math.ceil((yAxisMax * 1.1) / 50) * 50 : 100,
                        ticks: {
                            font: { size: 12, family: "'Poppins', sans-serif", weight: '500' },
                            padding: 10,
                            callback: (value) => value + ' pts'
                        },
                        grid: { color: 'rgba(226, 232, 240, 1)', drawBorder: false },
                        border: { display: false }
                    },
                    y: { // Category axis
                        grid: { display: false },
                        ticks: {
                            font: { size: 13, family: "'Poppins', sans-serif", weight: '600' },
                            padding: 10
                        },
                        border: { display: false }
                    }
                },
                layout: {
                    padding: { top: 10, right: 20, bottom: 10, left: 10 }
                }
            }
        });
        canvas.addEventListener('mousemove', (e) => {
            const activePoints = window.studentTaskChart.getElementsAtEventForMode(e, 'nearest', { intersect: true }, true);
            canvas.style.cursor = activePoints.length ? 'pointer' : 'default';
        });
    } catch (error) {
        console.error('Error creating chart:', error);
    }
}

function switchTier(button, tier) {
    // Update active button styling
    document.querySelectorAll('.tier-btn').forEach(btn => {
        btn.classList.remove('bg-white', 'text-sky-600', 'shadow');
        btn.classList.add('text-gray-600', 'hover:bg-gray-200');
    });
    button.classList.add('bg-white', 'text-sky-600', 'shadow');
    button.classList.remove('text-gray-600', 'hover:bg-gray-200');

    const modalContainer = document.querySelector('#studentTaskDataModal .relative');
    const studentId = modalContainer.dataset.studentId;
    
    if (studentId) {
        fetchStudentTaskData(studentId, tier);
    } else {
        console.error('Student ID not found');
    }
}

function closeModal() {
    const modal = document.getElementById('studentTaskDataModal');
    const modalContainer = modal.querySelector('.relative');
    
    if (modal && modalContainer) {
        modalContainer.classList.remove('opacity-100', 'scale-100');
        modalContainer.classList.add('opacity-0', 'scale-95');
        
        setTimeout(() => {
            modal.classList.add('hidden');
        }, 200);
    }
}

document.addEventListener('htmx:afterSwap', function(event) {
    document.querySelectorAll('[onclick^="viewDetails"]').forEach(button => {
        const studentId = button.getAttribute('data-student-id');
        button.onclick = () => viewDetails(studentId);
    });

    const modal = document.getElementById('studentTaskDataModal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                closeModal();
            }
        });

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
                closeModal();
            }
        });
    }
});