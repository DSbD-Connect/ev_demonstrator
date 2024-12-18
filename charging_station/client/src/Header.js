import React, { useState, useEffect } from 'react';


/*
    Adopted the following weathercode to icon logic from:
    https://github.com/Leftium/weather-sense

*/
function wmoInterpretation(color, description, icon) {
	color = color || '#9E9200';
	icon = `icons/airy/${icon}@4x.png`;


	return {
		description,
		color,
		icon
	};
}

export const WMO_CODES= {
	0: wmoInterpretation('#F1F1F1', 'Clear', 'clear'),

	1: wmoInterpretation('#E2E2E2', 'Mostly Clear', 'mostly-clear'),
	2: wmoInterpretation('#C6C6C6', 'Partly Cloudy', 'partly-cloudy'),
	3: wmoInterpretation('#ABABAB', 'Overcast', 'overcast'),

	45: wmoInterpretation('#A4ACBA', 'Fog', 'fog'),
	48: wmoInterpretation('#8891A4', 'Icy Fog', 'rime-fog'),

	51: wmoInterpretation('#3DECEB', 'Light Drizzle', 'light-drizzle'),
	53: wmoInterpretation('#0CCECE', 'Drizzle', 'moderate-drizzle'),
	55: wmoInterpretation('#0AB1B1', 'Heavy Drizzle', 'dense-drizzle'),

	80: wmoInterpretation('#9BCCFD', 'Light Showers', 'light-rain'),
	81: wmoInterpretation('#51B4FF', 'Showers', 'moderate-rain'),
	82: wmoInterpretation('#029AE8', 'Heavy Showers', 'heavy-rain'),

	61: wmoInterpretation('#BFC3FA', 'Light Rain', 'light-rain'),
	63: wmoInterpretation('#9CA7FA', 'Rain', 'moderate-rain'),
	65: wmoInterpretation('#748BF8', 'Heavy Rain', 'heavy-rain'),

	56: wmoInterpretation('#D3BFE8', 'Light Freezing Drizzle', 'light-freezing-drizzle'),
	57: wmoInterpretation('#A780D4', 'Freezing Drizzle', 'dense-freezing-drizzle'),

	66: wmoInterpretation('#CAC1EE', 'Light Freezing Rain', 'light-freezing-rain'),
	67: wmoInterpretation('#9486E1', 'Freezing Rain', 'heavy-freezing-rain'),

	71: wmoInterpretation('#F9B1D8', 'Light Snow', 'slight-snowfall'),
	73: wmoInterpretation('#F983C7', 'Snow', 'moderate-snowfall'),
	75: wmoInterpretation('#F748B7', 'Heavy Snow', 'heavy-snowfall'),

	77: wmoInterpretation('#E7B6EE', 'Snow Grains', 'snowflake'),

	85: wmoInterpretation('#E7B6EE', 'Light Snow Showers', 'slight-snowfall'),
	86: wmoInterpretation('#CD68E0', 'Snow Showers', 'heavy-snowfall'),

	95: wmoInterpretation('#525F7A', 'Thunderstorm', 'thunderstorm'),

	96: wmoInterpretation('#3D475C', 'Light T-storm w/ Hail', 'thunderstorm-with-hail'),
	99: wmoInterpretation('#2A3140', 'T-storm w/ Hail', 'thunderstorm-with-hail')
};

const wmoCode = (code) =>
{
	if (code !== undefined) {
		return WMO_CODES[code];
	}
	return {
		description: '...',
		icon: ''
	};
}

const getWeatherData = async () => {
    // Replace with actual API call if needed
    const weather_url = "https://api.open-meteo.com/v1/forecast?latitude=51.7462&longitude=-1.2734&current=temperature_2m,apparent_temperature,rain,weather_code&hourly=temperature_80m&forecast_days=1"
    
    var icon= '' // Example weather icon
    var temperature= '25°C' // Example temperature
  
      try {
        const response = await fetch(weather_url); 
        if (!response.ok) {
          throw new Error('Error in fetching weather data');
        }
        
        const weather_result = await response.json()
        
        icon = wmoCode(weather_result["current"]["weather_code"]).icon;
        temperature = weather_result["current"]["temperature_2m"] +"°C";
        console.log(icon);
        console.log(temperature);
  
      } catch (error) {
        console.error(error);
      }
      return {
          icon,
          temperature
      };
  };

const Header = () => {
  const [weather, setWeather] = useState({"icon": "", "temperature":""});
  const [currentTime, setCurrentTime] = useState('');

  useEffect(() => {
    const fetchWeather = async () => {
      const weather_data = await getWeatherData();
      setWeather(weather_data);
    };

    // Update the current time and weather every minute
    const interval = setInterval(async () => {
      const now = new Date();
      setCurrentTime(now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: true }).toUpperCase());
      fetchWeather();
    }, 60000); // Update every minute

    // Initial time setting
    setCurrentTime(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: true }).toUpperCase());
    fetchWeather();
    return () => clearInterval(interval); // Cleanup on unmount

  }, []);

  return (
    <div className="header" style={styles.header}>
      <div style={styles.welcomeText}>Welcome</div>
      <div style={styles.rightContainer}>
        <div style={styles.weatherContainer}>
          <img src={weather["icon"]} style={styles.weatherIcon} />
          <span style={styles.temperature}>{weather["temperature"]}</span>
        </div>
        <div style={styles.divider}></div>
        <div style={styles.time}>{currentTime}</div>
      </div>
    </div>
  );
};


const styles = {
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '10px 20px',
    borderRadius: '8px',
    maxWidth: '800px',
    background: "#ffffff",
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
    fontFamily: 'Roboto-Medium, sans-serif',
    objectFit: 'cover',
    margin: '20px',
    width: 'calc(100% - 40px)'
    
  },
  welcomeText: {
    flexGrow: 1,
    textAlign: 'left', 
    fontSize: '32px'
    
  },
  rightContainer: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'flex-end', 
  },
  weatherContainer: {
    display: 'flex',
    alignItems: 'center',
    marginRight: '10px', 
  },
  weatherIcon: {
    fontSize: '32px',
    height: '32px',
    marginRight: '5px',
    display: 'inline-block'
  },
  temperature: {
    fontSize: '32px',
    color : 'grey',
  },
  time: {
    fontSize: '32px',
    color : 'grey',

  },
  divider: {
    width: '1px', // Divider width
    height: '32px', // Divider height
    backgroundColor: '#ccc', // Divider color
    margin: '0 10px', // Space around the divider
  },
};

export default Header;