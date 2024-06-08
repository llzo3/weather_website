document.addEventListener('DOMContentLoaded', (event) => {
    var map = L.map('map', {
        maxBounds: [
            [-60, -180],
            [60, 180]
        ],
        minZoom: 2,
        maxBoundsViscosity: 1.0
    }).setView([37.5665, 126.9780], 2);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
    }).addTo(map);

    function onMapClick(e) {
        fetchWeather(e.latlng.lat, e.latlng.lng);
    }

    map.on('click', onMapClick);

    document.querySelectorAll('.history-item').forEach(item => {
        item.addEventListener('click', () => {
            fetchWeather(item.dataset.lat, item.dataset.lon);
        });
    });

    document.querySelectorAll('.favorite-item').forEach(item => {
        item.addEventListener('click', () => {
            fetchWeather(item.dataset.lat, item.dataset.lon);
        });
    });

    function fetchWeather(lat, lon) {
        fetch(`/weather?lat=${lat}&lon=${lon}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('weather-header').textContent = `${data.city} 기상환경`;
                document.getElementById('current-weather').innerHTML = `
                    <div>기온: ${data.current.temperature}°C</div>
                    <div>체감 온도: ${data.current.feels_like}°C</div>
                    <div>최저 기온: ${data.current.temp_min}°C</div>
                    <div>최고 기온: ${data.current.temp_max}°C</div>
                    <div>날씨 설명: ${data.current.description}</div>
                    <div>습도: ${data.current.humidity}%</div>
                    <div>풍속: ${data.current.wind_speed} m/s</div>
                    <div>기압: ${data.current.pressure} hPa</div>
                    <div>자외선 지수: ${data.current.uv_index}</div>
                    <div>일출: ${data.current.sunrise}</div>
                    <div>일몰: ${data.current.sunset}</div>
                    <div>현지 시간: ${data.current.date}</div>
                    <div>한국 시간: ${data.current.korea_time}</div>
                    <div>한국과의 시차: ${data.current.timezone_diff}시간</div>
                `;
                document.getElementById('hourly-weather').innerHTML = data.hourly.map(hour => `
                    <div class="hourly">
                        <div>${hour.time}</div>
                        <div>${hour.temperature}°C</div>
                        <div>${hour.description}</div>
                    </div>
                `).join('');
                document.getElementById('daily-weather').innerHTML = data.daily.map(day => `
                    <div class="daily">
                        <div>${day.date}</div>
                        <div>${day.temperature.day}°C (최고: ${day.temperature.max}°C, 최저: ${day.temperature.min}°C)</div>
                        <div>${day.description}</div>
                    </div>
                `).join('');
                document.body.style.backgroundImage = getBackgroundImage(data.current.is_day);
            })
            .catch(error => {
                console.error('Error fetching weather data:', error);
            });
    }

    function getImageForWeather(description) {
        if (description.includes('맑음')) {
            return 'day.png';
        } else if (description.includes('비')) {
            return 'rainy.png';
        } else if (description.includes('눈')) {
            return 'snowy.png';
        } else if (description.includes('구름')) {
            return 'cloudy.png';
        } else if (description.includes('더움')) {
            return 'hot.png';
        } else if (description.includes('따뜻함')) {
            return 'warm.png';
        } else if (description.includes('선선함')) {
            return 'cool.png';
        } else if (description.includes('추움')) {
            return 'cold.png';
        } else {
            return 'day.png';
        }
    }

    function getBackgroundImage(is_day) {
        if (is_day) {
            return "linear-gradient(to bottom, #87CEEB, #ffffff)";
        } else {
            return "linear-gradient(to bottom, #2c3e50, #bdc3c7)";
        }
    }

    window.addToFavorites = function(lat, lon) {
        fetch(`/favorites?lat=${lat}&lon=${lon}`, { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
            });
    }
});
