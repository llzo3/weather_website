const dateCardWrapper = document.querySelector(".date-card-wrapper");
const datePicker = document.querySelector("#date-picker");
const title = document.querySelector("#title");
const weatherInfo = document.querySelector("#weather-info");
const weatherImg = document.querySelector("#weather-img");
const personImg = document.querySelector("#person-img");
const body = document.querySelector("body");

function timestampToDate(timestamp) {
    const fullDate = new Date(timestamp * 1000);
  
    const month = fullDate.getMonth() + 1;
    const date = fullDate.getDate();
  
    return `${month}월 ${date}일`;
}

function getWeatherImage(weather, feels_like) {
    if (weather.includes("rain")) {
        return "/static/images/rainy.png";
    } else if (weather.includes("snow")) {
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

function updateBackground(sunrise, sunset) {
    const currentTime = new Date();
    if (currentTime >= sunrise && currentTime < sunset) {
        body.style.backgroundImage = "url('/static/images/day.jpg')";
    } else {
        body.style.backgroundImage = "url('/static/images/night.jpg')";
    }
}

function fetchWeather(lat, lon) {
    fetch(`/weather?lat=${lat}&lon=${lon}`)
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('weather-container');
            const header = document.getElementById('weather-header');
            const details = document.getElementById('weather-details');
            
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

            const sunrise = new Date(data.sunrise);
            const sunset = new Date(data.sunset);
            updateBackground(sunrise, sunset);
            weatherImg.src = getWeatherImage(data.description, data.feels_like);
        });
}

// 초기 위치 설정
const lat = 37.477550020716194;
const lon = 126.98212524649105;
fetchWeather(lat, lon);

document.querySelectorAll('.history-item').forEach(item => {
    item.addEventListener('click', function() {
        const lat = this.getAttribute('data-lat');
        const lon = this.getAttribute('data-lon');
        fetchWeather(lat, lon);
    });
});
