document.addEventListener('DOMContentLoaded', (event) => {
    var map = L.map('map', {
        maxBounds: [
            [-85, -180],
            [85, 180]
        ],
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
                document.getElementById('weather-details').innerHTML = `
                    기온: ${data.temperature}°C<br>
                    체감 온도: ${data.feels_like}°C<br>
                    최저 기온: ${data.temp_min}°C<br>
                    최고 기온: ${data.temp_max}°C<br>
                    날씨 설명: ${data.description}<br>
                    습도: ${data.humidity}%<br>
                    풍속: ${data.wind_speed} m/s<br>
                    기압: ${data.pressure} hPa<br>
                    자외선 지수: ${data.uv_index}<br>
                    일출: ${data.sunrise}<br>
                    일몰: ${data.sunset}<br>
                    현지 시간: ${data.date}<br>
                    한국 시간: ${data.korea_time}<br>
                    한국과의 시차: ${data.timezone_diff}시간
                `;
                document.getElementById('weather-img').src = `/static/images/${getImageForWeather(data.description)}`;
                document.getElementById('weather-img').alt = data.description; // alt 속성 설정
                document.body.style.backgroundImage = getBackgroundImage();
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

    function getBackgroundImage() {
        const hour = new Date().getHours();
        if (hour >= 6 && hour < 18) {
            return "url('/static/images/day.png')";
        } else {
            return "url('/static/images/night.png')";
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
