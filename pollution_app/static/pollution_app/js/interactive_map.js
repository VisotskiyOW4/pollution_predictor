
const map = L.map('map').setView([48.4, 31.2], 6);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; OpenStreetMap'
}).addTo(map);

let lineChart = null;
let barChart = null;
const riverMarkers = {}; // словник для оновлення маркерів

function getFuzzyColor(value) {
  const red = Math.min(255, Math.floor(255 * value));
  const green = Math.min(255, Math.floor(255 * (1 - value)));
  return `rgb(${red},${green},0)`;
}

function drawCharts(data, riverName) {
  const labels = data.forecast.map((_, i) => `${i + 1}-й місяць`);

  if (lineChart) lineChart.destroy();
  if (barChart) barChart.destroy();

  const lineCtx = document.getElementById('lineChart').getContext('2d');
  const barCtx = document.getElementById('barChart').getContext('2d');

  lineChart = new Chart(lineCtx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: `Рівень забруднення (лінійний графік)`,
        data: data.forecast,
        borderColor: 'rgba(75, 192, 192, 1)',
        tension: 0.3,
        fill: false
      }]
    }
  });

  barChart = new Chart(barCtx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: `Рівень забруднення (стовпчики)`,
        data: data.forecast,
        backgroundColor: 'rgba(54, 162, 235, 0.5)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1
      }]
    },
    options: {
      scales: {
        y: { beginAtZero: true, max: 1 }
      }
    }
  });
}

function loadGraphs(riverId, riverName) {
  document.getElementById('formRiverId').value = riverId;
  fetch(`/api/predictions/?river_id=${riverId}`)
    .then(response => response.json())
    .then(data => {
      document.getElementById('graphs').classList.remove('d-none');
      document.getElementById('riverName').innerText = riverName;
      drawCharts(data, riverName);
    });
}

fetch("/api/rivers/")
  .then(response => response.json())
  .then(rivers => {
    rivers.forEach(river => {
      fetch(`/api/predictions/?river_id=${river.id}`)
        .then(response => response.json())
        .then(data => {
          const forecast = data.forecast;
          const avgPollution = forecast.reduce((sum, x) => sum + x, 0) / forecast.length;

          const markerColor = getFuzzyColor(avgPollution);

          const marker = L.circleMarker([river.lat, river.lon], {
            radius: 10,
            color: markerColor,
            fillColor: markerColor,
            fillOpacity: 0.8
          }).addTo(map);

          marker.bindPopup(
            `<b>${river.name}</b><br>${river.description}<br><button class='btn btn-sm btn-primary mt-2' onclick='loadGraphs(${river.id}, "${river.name}")'>Показати графіки</button>`
          );

          riverMarkers[river.id] = marker;
        });
    });
  });

const form = document.getElementById('predictionForm');
form.addEventListener('submit', function(e) {
  e.preventDefault();
  const riverId = document.getElementById('formRiverId').value;
  const payload = {
    river_id: riverId,
    temperature: parseFloat(document.getElementById('temp').value),
    ph: parseFloat(document.getElementById('ph').value),
    nitrogen: parseFloat(document.getElementById('nitrogen').value),
    flow_speed: parseFloat(document.getElementById('flow').value)
  };

  fetch('/api/predict/', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(payload)
  })
  .then(response => response.json())
  .then(data => {
    document.getElementById('riverName').innerText = data.river;
    drawCharts(data, data.river);

    // оновити колір маркера
    fetch(`/api/predictions/?river_id=${riverId}`)
      .then(response => response.json())
      .then(predData => {
        const forecast = predData.forecast;
        const avg = forecast.reduce((sum, x) => sum + x, 0) / forecast.length;
        const newColor = getFuzzyColor(avg);

        if (riverMarkers[riverId]) {
          riverMarkers[riverId].setStyle({
            color: newColor,
            fillColor: newColor
          });
        }
      });
  });
});
