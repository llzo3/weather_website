const dateCardWrapper = document.querySelector(".date-card-wrapper");
const datePicker = document.querySelector("#date-picker");
const title = document.querySelector("#title");
const weatherInfo = document.querySelector("#weather-info");
const weatherImg = document.querySelector("#weather-img");
const personImg = document.querySelector("#person-img");
const body = document.querySelector("body");

function timestampToDate(timestamp, timezoneOffset) {
    const fullDate = new Date((timestamp + timezoneOffset) * 1000);
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

function updateBackground(sunrise, sunset, timezoneOffset) {
    const currentTime = new Date().getTime() / 1000;
    const localTime = currentTime + timezoneOffset;
    if (localTime >= sunrise && localTime < sunset) {
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
                일출: ${new Date((data.sunrise + data.timezone) * 1000).toLocaleTimeString()}<br>
                일몰: ${new Date((data.sunset + data.timezone) * 1000).toLocaleTimeString()}
            `;

            const sunrise = data.sunrise + data.timezone;
            const sunset = data.sunset + data.timezone;
            const timezoneOffset = data.timezone;

            updateBackground(sunrise, sunset, timezoneOffset);
            weatherImg.src = getWeatherImage(data.description, data.feels_like);
        });
}

// 초기 위치로 날씨 정보를 가져옵니다.
fetchWeather(37.477550020716194, 126.98212524649105);

// 위도 경도 입력 (기본 서울 위치)
const lat = 37.477550020716194;
const lon = 126.98212524649105;

fetch(
    `https://api.openweathermap.org/data/2.5/onecall?lat=${lat}&lon=${lon}&exclude=minutely,hourly&units=metric&appId=YOUR_API_KEY`
)
.then(function (response) {
    return response.json();
})
.then(function (data) {
    const curr = data.current;
    const currTimestamp = curr.dt;
    const currTemp = Math.round(curr.temp);
    const currWeather = curr.weather[0].description;

    const today = {
        date: timestampToDate(currTimestamp, data.timezone_offset),
        tem: currTemp,
        weather: currWeather,
    };

    updateScreen(today);

    const daily = data.daily;
    let dailyList = [];

    for (let i = 1; i < daily.length; i++) {
        const dailyTimestamp = daily[i].dt;
        const dailyTemp = Math.round(daily[i].temp.day);
        const dailyWeather = daily[i].weather[0].description;

        dailyList.push({
            date: timestampToDate(dailyTimestamp, data.timezone_offset),
            tem: dailyTemp,
            weather: dailyWeather,
        });
    }

    datePicker.addEventListener("click", function () {
        dateCardWrapper.classList.toggle("hidden");
    });

    for (let i = 0; i < dailyList.length; i++) {
        const dateOption = document.createElement("div");
        dateOption.classList.add("date-card");
        dateOption.innerHTML = dailyList[i].date;
        dateOption.addEventListener("click", (e) => {
            updateScreen(dailyList[i]);
            dateCardWrapper.classList.toggle("hidden");
            window.scroll({ top: 0, behavior: "smooth" });
        });
        dateCardWrapper.appendChild(dateOption);
    }
});
