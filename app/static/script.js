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
                
                let weatherDetailsHTML = `
                    <table class="weather-details-table">
                        <tr><th>기온</th><td>${data.temperature}°C</td></tr>
                        <tr><th>체감 온도</th><td>${data.feels_like}°C</td></tr>
                        <tr><th>최저 기온</th><td>${data.temp_min}°C</td></tr>
                        <tr><th>최고 기온</th><td>${data.temp_max}°C</td></tr>
                        <tr><th>날씨 설명</th><td>${data.description}</td></tr>
                        <tr><th>습도</th><td>${data.humidity}%</td></tr>
                        <tr><th>풍속</th><td>${data.wind_speed} m/s</td></tr>
                        <tr><th>기압</th><td>${data.pressure} hPa</td></tr>
                        <tr><th>강수량</th><td>${data.rain} mm</td></tr>
                        <tr><th>자외선 지수</th><td>${data.uv_index}</td></tr>
                        <tr><th>일출</th><td>${data.sunrise}</td></tr>
                        <tr><th>일몰</th><td>${data.sunset}</td></tr>
                        <tr><th>현지 시간</th><td>${data.date}</td></tr>
                        <tr><th>한국 시간</th><td>${data.korea_time}</td></tr>
                        <tr><th>한국과의 시차</th><td>${data.timezone_diff}시간</td></tr>
                    </table>
                `;
                document.getElementById('weather-details').innerHTML = weatherDetailsHTML;
                document.getElementById('weather-img').src = `/static/images/${getImageForWeather(data.description)}`;
                document.getElementById('weather-img').alt = data.description;
                document.body.style.backgroundImage = getBackgroundImage();

                let forecastHTML = '<table class="forecast-table"><tr><th>날짜</th><th>시간</th><th>기온</th><th>체감 온도</th><th>최저 기온</th><th>최고 기온</th><th>날씨 설명</th><th>습도</th><th>풍속</th><th>강수량</th><th>강수 확률</th></tr>';
                let currentDate = '';
                data.forecast.forEach(item => {
                    let date = item.date.split(' ')[0];
                    let time = item.date.split(' ')[1];
                    if (currentDate !== date) {
                        currentDate = date;
                        forecastHTML += `<tr><td colspan="11" class="date-row">${date}</td></tr>`;
                    }
                    forecastHTML += `
                        <tr>
                            <td>${date}</td>
                            <td>${time}</td>
                            <td>${item.temperature}°C</td>
                            <td>${item.feels_like}°C</td>
                            <td>${item.temp_min}°C</td>
                            <td>${item.temp_max}°C</td>
                            <td>${item.description}</td>
                            <td>${item.humidity}%</td>
                            <td>${item.wind_speed} m/s</td>
                            <td>${item.rain} mm</td>
                            <td>${item.pop}%</td>
                        </tr>
                    `;
                });
                forecastHTML += '</table>';
                document.getElementById('forecast-details').innerHTML = forecastHTML;
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

    window.removeFromFavorites = function(lat, lon) {
        fetch(`/favorites?lat=${lat}&lon=${lon}`, { method: 'DELETE' })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                location.reload();
            });
    }
});
