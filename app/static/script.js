var map = L.map('map').setView([0, 0], 2);  // 전세계 지도로 초기 설정
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

            header.textContent = `${data.city}의 ${data.date}
