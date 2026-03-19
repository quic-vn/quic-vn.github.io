document.addEventListener('DOMContentLoaded', function () {
    const ctx = document.getElementById('quicChart').getContext('2d');

    // --- Data ---
    const ipv4Data = {
        labels: ['Jan 2025', 'Oct 2025', 'Feb 2026'],
        bar: {
            label: 'QUIC-enabled IPv4 Addresses',
            data: [8337, 17278, 17691],
        },
        line: {
            label: 'Percentage of Total IPv4 enabled QUIC (%)',
            data: [0.05, 0.11, 0.11],
        },
        yAxisLabel: 'Number of Addresses',
        chartTitle: 'Growth of QUIC Adoption in Vietnam (IPv4)',
    };

    // IPv6: Jan 2025 & Oct 2025 = no stats (null), Feb 2026 = 3518
    const ipv6Data = {
        labels: ['Jan 2025', 'Oct 2025', 'Feb 2026'],
        bar: {
            label: 'QUIC-enabled IPv6 Addresses (hitlist)',
            data: [null, null, 3518],
        },
        line: {
            label: 'Percentage of Total IPv6 enabled QUIC (%)',
            data: [null, null, 0.3944], // 3518 / 891685 * 100 ≈ 0.3944%
        },
        yAxisLabel: 'Number of Addresses',
        chartTitle: 'Growth of QUIC Adoption in Vietnam (IPv6)',
    };

    let currentMode = 'ipv4'; // 'ipv4' | 'ipv6'

    // --- Custom plugin: draws sample-size badge inside chart area ---
    const sampleSizeBadgePlugin = {
        id: 'sampleSizeBadge',
        afterDraw(chart) {
            const opts = chart.options.plugins.sampleSizeBadge;
            if (!opts || !opts.display) return;

            const { ctx, chartArea: { left, top, right } } = chart;
            const text1 = 'Total IPv6 (hitlist)';
            const text2 = opts.total;

            const pad = { x: 12, y: 8 };
            const lineGap = 4;

            ctx.save();

            // Measure text
            ctx.font = 'bold 11px "Helvetica Neue", Helvetica, Arial, sans-serif';
            const w1 = ctx.measureText(text1).width;
            ctx.font = 'bold 15px "Helvetica Neue", Helvetica, Arial, sans-serif';
            const w2 = ctx.measureText(text2).width;

            const boxW = Math.max(w1, w2) + pad.x * 2;
            const boxH = 11 + lineGap + 15 + pad.y * 2;
            const bx = left + 12;
            const by = top + 12;
            const radius = 6;

            // Draw rounded rect background
            ctx.beginPath();
            ctx.moveTo(bx + radius, by);
            ctx.lineTo(bx + boxW - radius, by);
            ctx.quadraticCurveTo(bx + boxW, by, bx + boxW, by + radius);
            ctx.lineTo(bx + boxW, by + boxH - radius);
            ctx.quadraticCurveTo(bx + boxW, by + boxH, bx + boxW - radius, by + boxH);
            ctx.lineTo(bx + radius, by + boxH);
            ctx.quadraticCurveTo(bx, by + boxH, bx, by + boxH - radius);
            ctx.lineTo(bx, by + radius);
            ctx.quadraticCurveTo(bx, by, bx + radius, by);
            ctx.closePath();
            ctx.fillStyle = 'rgba(72, 199, 142, 0.15)';
            ctx.fill();
            ctx.strokeStyle = 'rgba(72, 199, 142, 0.6)';
            ctx.lineWidth = 1.2;
            ctx.stroke();

            const cx = bx + boxW / 2;

            // Label row
            ctx.fillStyle = '#555';
            ctx.font = '11px "Helvetica Neue", Helvetica, Arial, sans-serif';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'top';
            ctx.fillText(text1, cx, by + pad.y);

            // Value row
            ctx.fillStyle = '#2d6a4f';
            ctx.font = 'bold 15px "Helvetica Neue", Helvetica, Arial, sans-serif';
            ctx.fillText(text2, cx, by + pad.y + 11 + lineGap);

            ctx.restore();
        }
    };

    Chart.register(sampleSizeBadgePlugin);

    // --- Chart Config ---
    function buildChartData(d) {
        return {
            labels: d.labels,
            datasets: [
                {
                    type: 'bar',
                    label: d.bar.label,
                    data: d.bar.data,
                    backgroundColor: currentMode === 'ipv4'
                        ? 'rgba(54, 162, 235, 0.8)'
                        : 'rgba(72, 199, 142, 0.8)',
                    borderColor: currentMode === 'ipv4'
                        ? 'rgba(54, 162, 235, 1)'
                        : 'rgba(72, 199, 142, 1)',
                    borderWidth: 1,
                    yAxisID: 'y',
                    order: 2,
                    spanGaps: false,
                },
                {
                    type: 'line',
                    label: d.line.label,
                    data: d.line.data,
                    borderColor: '#FF6384',
                    backgroundColor: '#FF6384',
                    borderWidth: 2,
                    tension: 0,
                    fill: false,
                    pointBackgroundColor: '#FF6384',
                    yAxisID: 'y1',
                    order: 1,
                    spanGaps: false,
                }
            ]
        };
    }

    const config = {
        data: buildChartData(ipv4Data),
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        font: {
                            family: "'Helvetica Neue', 'Helvetica', 'Arial', sans-serif",
                            size: 12,
                            weight: 'bold'
                        },
                    }
                },
                title: {
                    display: true,
                    text: ipv4Data.chartTitle,
                    font: {
                        size: 16,
                        family: "'Helvetica Neue', 'Helvetica', 'Arial', sans-serif",
                        weight: 'bold'
                    },
                    padding: {
                        top: 10,
                        bottom: 30
                    }
                },
                sampleSizeBadge: {
                    display: false,
                    total: ''
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function (context) {
                            const val = context.parsed.y;
                            if (val === null || val === undefined) {
                                return context.dataset.label + ': No statistics available';
                            }
                            return context.dataset.label + ': ' + val.toLocaleString();
                        }
                    }
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

    const chart = new Chart(ctx, config);

    // --- Switch Logic ---
    const btnIPv4 = document.getElementById('switchIPv4');
    const btnIPv6 = document.getElementById('switchIPv6');
    const chartDescription = document.getElementById('chartDescription');

    function switchChart(mode) {
        currentMode = mode;
        const d = mode === 'ipv4' ? ipv4Data : ipv6Data;

        // Update data
        chart.data = buildChartData(d);

        // Update title & in-chart badge
        chart.options.plugins.title.text = d.chartTitle;
        if (mode === 'ipv6') {
            chart.options.plugins.sampleSizeBadge.display = true;
            chart.options.plugins.sampleSizeBadge.total = '891,685';
        } else {
            chart.options.plugins.sampleSizeBadge.display = false;
        }

        chart.options.scales.y1.display = true;

        chart.update();

        // Update button states
        if (btnIPv4 && btnIPv6) {
            if (mode === 'ipv4') {
                btnIPv4.classList.add('active');
                btnIPv6.classList.remove('active');
            } else {
                btnIPv6.classList.add('active');
                btnIPv4.classList.remove('active');
            }
        }

        // Update description text
        if (chartDescription) {
            if (mode === 'ipv4') {
                chartDescription.textContent = 'The chart below illustrates the growth of QUIC-enabled IPv4 addresses in Vietnam.';
            } else {
                chartDescription.textContent = 'The chart below illustrates the growth of QUIC-enabled IPv6 addresses in Vietnam.';
            }
        }

        // Re-populate export selects with current dataset labels
        populateExportSelects(d);
    }

    if (btnIPv4) btnIPv4.addEventListener('click', () => switchChart('ipv4'));
    if (btnIPv6) btnIPv6.addEventListener('click', () => switchChart('ipv6'));

    // --- Export Functionality ---
    const singleDateSelect = document.getElementById('singleDateSelect');
    const startDateSelect = document.getElementById('startDateSelect');
    const endDateSelect = document.getElementById('endDateSelect');

    function populateExportSelects(d) {
        if (!singleDateSelect || !startDateSelect || !endDateSelect) return;
        [singleDateSelect, startDateSelect, endDateSelect].forEach(sel => {
            sel.innerHTML = '';
        });
        d.labels.forEach((label, index) => {
            const option = new Option(label, index);
            singleDateSelect.add(option.cloneNode(true));
            startDateSelect.add(option.cloneNode(true));
            endDateSelect.add(option.cloneNode(true));
        });
        endDateSelect.value = d.labels.length - 1;
    }

    // Initial population
    populateExportSelects(ipv4Data);

    function downloadCSV(filename, rows) {
        const blob = new Blob([rows.join('\n')], { type: 'text/csv;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    function getCSVData(indices) {
        const datasets = chart.data.datasets || [];
        const currentData = currentMode === 'ipv4' ? ipv4Data : ipv6Data;
        const header = ['Date', ...datasets.map(ds => ds.label || 'Series')];
        const rows = [header.join(',')];

        indices.forEach(i => {
            const label = currentData.labels[i];
            const row = [label, ...datasets.map(ds => {
                const v = Array.isArray(ds.data) ? ds.data[i] : '';
                if (v === null || v === undefined) return 'N/A';
                return typeof v === 'number' ? v : (v ?? '');
            })];
            rows.push(row.join(','));
        });
        return rows;
    }

    // Export Single Date
    const exportSingleBtn = document.getElementById('exportSingleBtn');
    if (exportSingleBtn) {
        exportSingleBtn.addEventListener('click', function () {
            const index = parseInt(singleDateSelect.value);
            const rows = getCSVData([index]);
            const currentData = currentMode === 'ipv4' ? ipv4Data : ipv6Data;
            const label = currentData.labels[index].replace(/\s+/g, '_');
            downloadCSV(`quic_${currentMode}_data_${label}.csv`, rows);
        });
    }

    // Export Range
    const exportRangeBtn = document.getElementById('exportRangeBtn');
    if (exportRangeBtn) {
        exportRangeBtn.addEventListener('click', function () {
            const start = parseInt(startDateSelect.value);
            const end = parseInt(endDateSelect.value);

            if (start > end) {
                alert('Start date must be before or equal to end date.');
                return;
            }

            const indices = [];
            for (let i = start; i <= end; i++) {
                indices.push(i);
            }

            const rows = getCSVData(indices);
            downloadCSV(`quic_${currentMode}_data_range.csv`, rows);
        });
    }
});
