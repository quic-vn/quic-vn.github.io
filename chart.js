document.addEventListener('DOMContentLoaded', function() {
    const ctx = document.getElementById('quicChart').getContext('2d');
    
    // Dummy data representing the growth of QUIC adoption
    // Replace this with actual data from your research results
    const data = {
        labels: ['Jan 2025', 'Mar 2025', 'May 2025', 'Jul 2025', 'Sep 2025', 'Oct 2025'],
        datasets: [
            {
                type: 'bar',
                label: 'QUIC-enabled IPv4 Addresses',
                data: [8337, 10500, 12800, 14200, 16100, 17278],
                backgroundColor: 'rgba(54, 162, 235, 0.8)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1,
                yAxisID: 'y',
                order: 2
            },
            {
                type: 'line',
                label: 'Percentage of Total IPv4 (%)',
                data: [0.05, 0.06, 0.08, 0.09, 0.10, 0.11],
                borderColor: '#FF6384',
                backgroundColor: '#FF6384',
                borderWidth: 2,
                tension: 0.4,
                fill: false,
                pointBackgroundColor: '#FF6384',
                yAxisID: 'y1',
                order: 1
            }
        ]
    };

    const config = {
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        font: {
                            family: "'Helvetica Neue', 'Helvetica', 'Arial', sans-serif",
                            size: 12
                        }
                    }
                },
                title: {
                    display: true,
                    text: 'Growth of QUIC Adoption in Vietnam (2025)',
                    font: {
                        size: 16,
                        family: "'Helvetica Neue', 'Helvetica', 'Arial', sans-serif"
                    },
                    padding: {
                        top: 10,
                        bottom: 30
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Addresses'
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Percentage (%)'
                    },
                    grid: {
                        drawOnChartArea: false
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            }
        },
    };

    new Chart(ctx, config);

    // Export chart data to CSV and download
    const exportBtn = document.getElementById('exportCsvBtn');
    if (exportBtn) {
        exportBtn.addEventListener('click', function () {
            const labels = config.data.labels || [];
            const datasets = config.data.datasets || [];

            const header = ['Date', ...datasets.map(ds => ds.label || 'Series')];
            const lines = [header.join(',')];

            for (let i = 0; i < labels.length; i++) {
                const row = [labels[i], ...datasets.map(ds => {
                    const v = Array.isArray(ds.data) ? ds.data[i] : '';
                    return typeof v === 'number' ? v : (v ?? '');
                })];
                lines.push(row.join(','));
            }

            const blob = new Blob([lines.join('\n')], { type: 'text/csv;charset=utf-8' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'quic_deployment_2025.csv';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        });
    }
});
