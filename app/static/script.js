const map = L.map('map').setView([37.5665, 126.9780], 10); // Default location is Seoul

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
}).addTo(map);

function updateBackground(sunrise, sunset) {
    const currentTime = new Date();
    if (currentTime >= sunrise && currentTime < sunset) {
        document.body.style.backgroundImage = "url('/static/images/day.jpg')";
    } else {
        document.body.style.backgroundImage = "url('/static/images/night.jpg')";
    }
}

function getWeatherImage(description, feels_like) {
    if (description.includes("rain")) {
        return "/static/images/rainy.png";
    } else if (description.includes("snow")) {
        return "/static/images/snowy.png";
    } else {
        if (feels_like > 30) {
            return "/static/images/hot.png";
        } else if (feels_like > 20) {
            return "/static/images/warm.png";
        } else if (feels_like > 10) {
            return "/static/images/cool.png";
        } else {
            return "/static/images/cold.png";
        }
    }
}

function fetchWeather(lat, lon) {
    fetch(`/weather?lat=${lat}&lon=${lon}`)
        .then(response => response.json())
        .then(data => {
            const header = document.getElementById('weather-header');
            const details = document.getElementById('weather-details');
            const weatherImg = document.getElementById('weather-img');

            header.textContent = `${data.city}의 ${data.date} 기상환경은?`;
            details.innerHTML = `
                온도: ${data.temperature}°C<br>
                체감온도: ${data.feels_like}°C<br>
                최소온도: ${data.temp_min}°C<br>
                최대온도: ${data.temp_max}°C<br>
                기상환경: ${data.description}<br>
                습도: ${data.humidity}%<br>
                풍속: ${data.wind_speed} m/s<br>
                기압: ${data.pressure} hPa<br>
                자외선지수: ${data.uv_index}<br>
                일출: ${data.sunrise}<br>
                일몰: ${data.sunset}
            `;

            const sunrise = new Date(`1970-01-01T${data.sunrise}Z`);
            const sunset = new Date(`1970-01-01T${data.sunset}Z`);
            updateBackground(sunrise, sunset);

            weatherImg.src = getWeatherImage(data.description, data.feels_like);
        });
}

map.on('click', function(e) {
    var coord = e.latlng;
    fetchWeather(coord.lat, coord.lng);
});

document.querySelectorAll('.history-item').forEach(item => {
    item.addEventListener('click', function() {
        const lat = this.getAttribute('data-lat');
        const lon = this.getAttribute('data-lon');
        fetchWeather(lat, lon);
    });
});

// Click handler for recent search history items
document.getElementById('history-list').addEventListener('click', function(e) {
    if (e.target && e.target.matches('li.history-item')) {
        const lat = e.target.getAttribute('data-lat');
        const lon = e.target.getAttribute('data-lon');
        fetchWeather(lat, lon);
    }
});
