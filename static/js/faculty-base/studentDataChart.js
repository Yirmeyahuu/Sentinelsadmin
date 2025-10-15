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

    // Update modal content without creating chart yet
    modalContainer.innerHTML = `
        <div class="p-6 w-full max-w-[800px] mx-auto">
            <div class="flex items-center justify-between mb-6">
                <h2 class="text-xl font-bold text-slate-800">Student Task Details</h2>
                <button onclick="closeModal()" class="text-slate-400 hover:text-slate-600 transition-colors duration-200">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>

            <!-- Tier Filter -->
            <div class="flex space-x-2 mb-6">
                <button onclick="switchTier('novice')" class="px-4 py-2 rounded-lg text-sm font-medium bg-sky-100 text-sky-700 hover:bg-sky-200 active-tier">Novice</button>
                <button onclick="switchTier('junior')" class="px-4 py-2 rounded-lg text-sm font-medium bg-slate-100 text-slate-600 hover:bg-slate-200">Junior</button>
                <button onclick="switchTier('senior')" class="px-4 py-2 rounded-lg text-sm font-medium bg-slate-100 text-slate-600 hover:bg-slate-200">Senior</button>
            </div>
            <div class="h-[400px] w-full">
                <canvas id="studentTaskChart" width="800" height="400"></canvas>
            </div>
        </div>
    `;

    // Store student ID for tier switching
    modalContainer.dataset.studentId = studentId;
}

async function fetchStudentTaskData(studentId, tier) {
    try {
        // Fix the URL path
        const response = await fetch(`/Faculty/student-data/modal/${studentId}/`);
        if (!response.ok) {
            throw new Error('Failed to fetch student data');
        }
        const data = await response.json();
        console.log('Fetched data:', data); // Add logging to debug
        
        // Initialize empty tier data if none exists
        const tierData = (data.task_details && data.task_details[tier]) ? data.task_details[tier] : {};
        console.log('Tier data:', tierData); // Add logging to debug
        
        renderTaskChart(tierData, tier);
    } catch (error) {
        console.error("Error fetching student data:", error);
        renderTaskChart({}, tier);
    }
}

function renderTaskChart(taskData, tier) {
    // Get the canvas element
    const canvas = document.getElementById('studentTaskChart');
    
    if (!canvas) {
        console.error('Canvas element not found');
        return;
    }

    // Get the 2d context
    const ctx = canvas.getContext('2d');

    // Clean up existing chart properly
    if (window.studentTaskChart && typeof window.studentTaskChart.destroy === 'function') {
        window.studentTaskChart.destroy();
    }
    
    // Reset the canvas
    canvas.width = canvas.parentElement.offsetWidth;
    canvas.height = canvas.parentElement.offsetHeight;

    // Define tasks for each tier
    const tasks = {
        novice: [
            "Novice_Task_1(Collect Books)", "Novice_Task_2(Collect USB)",
            "Novice_Task_3(QNA)", "Novice_Task_4_(Defeat Rootkit)"
        ],
        junior: [
            "Junior_Task_1(Collect Books)", "Junior_Task_2(QNA)",
            "Junior_Task_3(Collect USB)", "Junior_Task_4(Bellaso's QNA)",
            "Junior_Task_5(QNA)", "Junior_Task_6(Defeat Serpentix2)"
        ],
        senior: [
            "Senior_Task_1(Collect Books)", "Senior_Task_2(QNA)",
            "Senior_Task_3(Collect USB)", "Senior_Task_4(QNA)",
            "Senior_Task_5(QNA)", "Senior_Task_6(Defeat Rootkit2)"
        ]
    };

    // Ensure taskData is an object
    taskData = taskData || {};

    // Initialize arrays with default values
    const chartData = new Array(tasks[tier].length).fill(0);
    const labels = tasks[tier].map(task => task.split('(')[1].replace(')', ''));
    const completionDates = new Array(tasks[tier].length).fill(null);

    // Update data if available
    tasks[tier].forEach((taskName, index) => {
        if (taskData[taskName]) {
            chartData[index] = taskData[taskName].points || 0;
            completionDates[index] = taskData[taskName].completedAt;
        }
    });

    console.log('Chart data:', { labels, data: chartData });

    // Define custom colors for different task types
    const taskColors = {
        'Collect Books': 'rgba(59, 130, 246, 0.8)', // Blue
        'Collect USB': 'rgba(16, 185, 129, 0.8)',   // Green
        'QNA': 'rgba(245, 158, 11, 0.8)',          // Orange
        'Defeat Rootkit': 'rgba(239, 68, 68, 0.8)', // Red
        'Bellaso\'s QNA': 'rgba(168, 85, 247, 0.8)', // Purple
        'Defeat Serpentix2': 'rgba(236, 72, 153, 0.8)', // Pink
        'Defeat Rootkit2': 'rgba(220, 38, 38, 0.8)'  // Dark Red
    };

    // Get task type from label
    const getTaskType = (label) => {
        for (const type of Object.keys(taskColors)) {
            if (label.includes(type)) return type;
        }
        return 'Other';
    };

    // Create new chart with Chart.js constructor
    try {
        window.studentTaskChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Points',
                    data: chartData,
                    backgroundColor: labels.map(label => {
                        const taskType = getTaskType(label);
                        return taskColors[taskType] || 'rgba(156, 163, 175, 0.8)';
                    }),
                    borderColor: labels.map(label => {
                        const taskType = getTaskType(label);
                        return taskColors[taskType]?.replace('0.8', '1') || 'rgb(107, 114, 128)';
                    }),
                    borderWidth: 2,
                    borderRadius: 8,
                    barThickness: 40, // Increased thickness
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
                        display: true,
                        position: 'top',
                        labels: {
                            font: {
                                family: "'Poppins', sans-serif",
                                size: 12,
                                weight: '500'
                            },
                            padding: 20,
                            usePointStyle: true,
                            pointStyle: 'rectRounded'
                        }
                    },
                    tooltip: {
                        enabled: true,
                        backgroundColor: 'rgba(17, 24, 39, 0.95)',
                        titleFont: {
                            size: 14,
                            family: "'Poppins', sans-serif",
                            weight: 'bold'
                        },
                        bodyFont: {
                            size: 13,
                            family: "'Poppins', sans-serif"
                        },
                        padding: 16,
                        cornerRadius: 8,
                        displayColors: true,
                        boxWidth: 8,
                        boxHeight: 8,
                        boxPadding: 4,
                        callbacks: {
                            title: function(context) {
                                return `Task: ${context[0].label}`;
                            },
                            label: function(context) {
                                const index = context.dataIndex;
                                const completedAt = completionDates[index];
                                return [
                                    `Points: ${context.raw} / 5`,
                                    completedAt ? `Completed: ${new Date(completedAt).toLocaleString()}` : 'Not completed'
                                ];
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        min: 0,
                        max: 5,
                        ticks: {
                            stepSize: 1,
                            font: {
                                size: 12,
                                family: "'Poppins', sans-serif",
                                weight: '500'
                            },
                            padding: 10,
                            callback: function(value) {
                                return value + ' pts';
                            }
                        },
                        grid: {
                            color: 'rgba(226, 232, 240, 0.5)',
                            drawBorder: false,
                            lineWidth: 0.5
                        },
                        border: {
                            display: false
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            font: {
                                size: 12,
                                family: "'Poppins', sans-serif",
                                weight: '500'
                            },
                            maxRotation: 45,
                            minRotation: 45,
                            padding: 10
                        },
                        border: {
                            display: false
                        }
                    }
                },
                layout: {
                    padding: {
                        top: 30,
                        right: 25,
                        bottom: 25,
                        left: 25
                    }
                }
            }
        });
        // Add hover effect to bars
        canvas.addEventListener('mousemove', (e) => {
            const activePoints = window.studentTaskChart.getElementsAtEventForMode(e, 'nearest', { intersect: true }, true);
            canvas.style.cursor = activePoints.length ? 'pointer' : 'default';
        });
    } catch (error) {
        console.error('Error creating chart:', error);
    }
}
function switchTier(tier) {
    // Update active button styling
    document.querySelectorAll('[onclick^="switchTier"]').forEach(btn => {
        btn.classList.remove('bg-sky-100', 'text-sky-700');
        btn.classList.add('bg-slate-100', 'text-slate-600');
    });
    event.target.classList.remove('bg-slate-100', 'text-slate-600');
    event.target.classList.add('bg-sky-100', 'text-sky-700');

    // Get studentId from the modal container's dataset
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
        // Add fade out animation
        modalContainer.classList.remove('opacity-100', 'scale-100');
        modalContainer.classList.add('opacity-0', 'scale-95');
        
        // Hide modal after animation
        setTimeout(() => {
            modal.classList.add('hidden');
        }, 200);
    }
}


// Add HTMX after-swap handler
document.addEventListener('htmx:afterSwap', function(event) {
    // Reinitialize click handlers for view details buttons
    document.querySelectorAll('[onclick^="viewDetails"]').forEach(button => {
        const studentId = button.getAttribute('data-student-id');
        button.onclick = () => viewDetails(studentId);
    });

    // Reinitialize modal close functionality
    const modal = document.getElementById('studentTaskDataModal');
    if (modal) {
        // Close on backdrop click
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                closeModal();
            }
        });

        // Close on ESC key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
                closeModal();
            }
        });
    }
});