document.addEventListener('DOMContentLoaded', function() {
    const ctx = document.getElementById('quicChart').getContext('2d');
    
    // Dummy data representing the growth of QUIC adoption
    // Replace this with actual data from your research results
    const data = {
        labels: ['Jan 2025', 'Feb 2025', 'Mar 2025', 'Apr 2025', 'May 2025', 'Jun 2025', 'Jul 2025', 'Aug 2025', 'Sep 2025', 'Oct 2025', 'Nov 2025', 'Dec 2025'],
        datasets: [{
            label: 'QUIC-enabled IPv4 Addresses',
            data: [8337, 8410, 8560, 8820, 9150, 9500, 9980, 10450, 11100, 11800, 12500, 13200],
            borderColor: '#4BC0C0', // Teal color matching the theme likely
            backgroundColor: 'rgba(255, 255, 255, 0)',
            borderWidth: 2,
            tension: 0.4, // Smooth curve
            fill: true,
            pointBackgroundColor: '#fff',
            pointBorderColor: '#4BC0C0',
            pointHoverBackgroundColor: '#4BC0C0',
            pointHoverBorderColor: '#fff'
        }]
    };

    const config = {
        type: 'line',
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
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Addresses'
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
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
git remote add origin https://github.com/quic-vn/quic-vn.github.io.git