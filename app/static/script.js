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
    const sunriseTime = new Date(sunrise);
    const sunsetTime = new Date(sunset);

    if (currentTime >= sunriseTime && currentTime < sunsetTime) {
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

// 위도 경도 입력
const lat = 37.477550020716194;
const lon = 126.98212524649105;

fetch(
    `https://api.openweathermap.org/data/2.5/onecall?lat=${lat}&lon=${lon}&exclude=minutely,hourly&units=metric&appId=2fa3f03d3732cc2adffbdcc9cd0ff4af`
  )
    .then(function (response) {
      return response.json();
    })
    .then(function (data) {
      // data = API 호출 후 원본 데이터
  
      const curr = data.current;
      const currTimestamp = curr.dt;
      const currDate = timestampToDate(currTimestamp);
      const currTemp = Math.round(curr.temp);
      const currWeatherId = curr.weather[0].id;
  
      // 오늘의 기상정보 객체 생성
      const today = {
        date: currDate,
        tem: currTemp,
        weather: currWeatherId,
      };
  
      updateScreen(today);
  
      // +7일 데이터 받아오기
  
      const daily = data.daily;
      let dailyList = [];
  
      for (let i = 1; i < daily.length; i++) {
        const dailyTimestamp = daily[i].dt;
        const dailyDate = timestampToDate(dailyTimestamp);
        const dailyTemp = Math.round(daily[i].temp.day);
        const dailyWeatherId = daily[i].weather[0].id;
  
        dailyList.push({
          date: dailyDate,
          tem: dailyTemp,
          weather: dailyWeatherId,
        });
      }
  
      // 날짜 선택 드롭다운 버튼 클릭해서 옵션 열고 닫기
      datePicker.addEventListener("click", function () {
        dateCardWrapper.classList.toggle("hidden");
      });
  
      // 날짜 선택지 생성 및 이벤트 부착
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
