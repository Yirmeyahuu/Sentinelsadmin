document.addEventListener('DOMContentLoaded', function() {
    const canvas = document.getElementById('surveyPieChart');
    if (canvas) {
        const ctx = canvas.getContext('2d');

        // Enhanced data with modern color scheme and gradient effects
        const gradients = [
            createGradient(['#22C55E', '#059669']), // Green for SA
            createGradient(['#38BDF8', '#0EA5E9']), // Blue for A
            createGradient(['#A855F7', '#7C3AED']), // Purple for UD
            createGradient(['#F87171', '#DC2626']), // Red for D
            createGradient(['#EF4444', '#B91C1C'])  // Dark Red for SD
        ];

        function createGradient(colors) {
            const gradient = ctx.createLinearGradient(0, 0, 0, 400);
            gradient.addColorStop(0, colors[0]);
            gradient.addColorStop(1, colors[1]);
            return gradient;
        }

        const data = {
            labels: ['Strongly Agree', 'Agree', 'Undecided', 'Disagree', 'Strongly Disagree'],
            datasets: [{
                data: [46, 208, 286, 289, 41],
                backgroundColor: gradients,
                borderWidth: 2,
                borderColor: '#ffffff',
                hoverOffset: 15,
                offset: 5,
                hoverBorderWidth: 0
            }]
        };

        const config = {
            type: 'doughnut',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '60%',
                radius: '90%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            font: {
                                size: 13,
                                family: "'Poppins', sans-serif",
                                weight: '500'
                            },
                            usePointStyle: true,
                            pointStyle: 'circle',
                            generateLabels: function(chart) {
                                const data = chart.data;
                                return data.labels.map((label, i) => ({
                                    text: `${label} (${data.datasets[0].data[i]})`,
                                    fillStyle: gradients[i],
                                    strokeStyle: gradients[i],
                                    lineWidth: 0,
                                    hidden: false,
                                    index: i
                                }));
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(17, 24, 39, 0.95)',
                        titleFont: {
                            size: 14,
                            family: "'Poppins', sans-serif",
                            weight: '600'
                        },
                        bodyFont: {
                            size: 13,
                            family: "'Poppins', sans-serif"
                        },
                        padding: 12,
                        cornerRadius: 8,
                        displayColors: true,
                        usePointStyle: true,
                        animation: {
                            duration: 150
                        },
                        callbacks: {
                            label: function(context) {
                                const value = context.raw;
                                const total = context.dataset.data.reduce((acc, val) => acc + val, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return ` ${percentage}% (${value} students)`;
                            },
                            title: function(context) {
                                return context[0].label;
                            }
                        }
                    }
                },
                animation: {
                    animateScale: true,
                    animateRotate: true,
                    duration: 800,
                    easing: 'easeOutCubic',
                    onProgress: function(animation) {
                        if (animation.currentStep === animation.numSteps) {
                            drawCenterText(this);
                        }
                    }
                },
                hover: {
                    mode: 'nearest',
                    intersect: true,
                    animationDuration: 200
                },
                layout: {
                    padding: 20
                }
            }
        };

        // Create and render the chart
        const myChart = new Chart(ctx, config);

        // Center text drawing function
        function drawCenterText(chart) {
            const {ctx, width, height} = chart;
            const total = chart.data.datasets[0].data.reduce((sum, value) => sum + value, 0);

            ctx.save();
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';

            // Total Label
            ctx.font = `500 14px 'Poppins'`;
            ctx.fillStyle = '#6B7280';
            ctx.fillText('Total Responses', width / 2, height / 2 - 15);

            // Total Number
            ctx.font = `600 24px 'Poppins'`;
            ctx.fillStyle = '#111827';
            ctx.fillText(total, width / 2, height / 2 + 15);

            ctx.restore();
        }

        // Add interactivity
        ctx.canvas.addEventListener('mousemove', function(event) {
            const activePoints = myChart.getElementsAtEventForMode(event, 'nearest', { intersect: true }, true);
            ctx.canvas.style.cursor = activePoints.length ? 'pointer' : 'default';
        });
    }
});