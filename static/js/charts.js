const palette = ['#337052', '#c49152', '#719867', '#806444', '#a6b888', '#537c7d', '#d5b48a'];
const charts = JSON.parse(document.getElementById('chart-data').textContent);
document.querySelectorAll('canvas[data-chart]').forEach(canvas => {
  const [title, type, rows] = charts[Number(canvas.dataset.chart)];
  const labels = [...new Set(rows.map(row => row.label))];
  const series = [...new Set(rows.map(row => row.series))];
  const doughnut = type === 'doughnut';
  const datasets = series.map((unit, index) => {
    const values = new Map(rows.filter(row => row.series === unit).map(row => [row.label, Number(row.value)]));
    return {
      label: unit || title,
      data: labels.map(label => values.get(label) ?? (type === 'line' ? null : 0)),
      backgroundColor: doughnut ? palette : palette[index % palette.length],
      borderColor: doughnut ? '#fff' : palette[index % palette.length],
      ...(unit ? { xAxisID: 'x', yAxisID: 'unit' + index } : {}),
    };
  });
  const scales = doughnut ? {} : { x: { ticks: { autoSkip: true, maxTicksLimit: 12 } } };
  series.forEach((unit, index) => {
    if (unit) scales['unit' + index] = {
      type: 'linear', axis: 'y', beginAtZero: true,
      position: index ? 'right' : 'left', title: { display: true, text: unit },
      grid: { drawOnChartArea: index === 0 },
    };
  });
  new Chart(canvas, {
    type,
    data: { labels, datasets },
    options: { responsive: true, maintainAspectRatio: false, scales,
      plugins: { legend: { display: doughnut || Boolean(series[0]), position: 'bottom' } } },
  });
});
