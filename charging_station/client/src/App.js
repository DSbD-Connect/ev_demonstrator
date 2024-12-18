import React, { useEffect, useState } from 'react';
import { QRCodeSVG } from 'qrcode.react'; 
import Countdown from "react-countdown";
import { TypeAnimation } from 'react-type-animation';
import Carousel from './Carousel';
import Header from './Header';
import styles from './App.css';


function App() {
  const [sessionActive, setSessionActive] = useState(false);
  const [sessionInfo, setSessionInfo] = useState(null);
  const [sessionSummary, setSessionSummary] = useState(null);
  const [CPState, setCPState] = useState("");
  const [QRdata, setQRData] = useState("");
  

  const startSession = () => {
    setSessionActive(true);
    /*setSessionInfo({
      startTime: new Date().toLocaleTimeString(),
      duration: "01:30", 
      amountCharged: "15 kWh", 
    });*/
  };

  const stopSession = () => {
    if (sessionInfo) { // Conditional check
      setSessionActive(false);
      setSessionSummary(sessionInfo);
      setSessionInfo(null);
    }
  };

  const getDateReadable = (startTimestamp) => {
    const date = new Date(startTimestamp * 1000); 
    const day = date.getDate().toString().padStart(2, '0');
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const year = date.getFullYear().toString().slice(2); // get last two digits of year
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    const seconds = date.getSeconds().toString().padStart(2, '0');
    const readableDate = `${day}/${month}/${year} ${hours}:${minutes}:${seconds}`;
    return readableDate;
  }
  const getDuration = (startTimeTimestamp) => {
    //const startTimeString = result.session_status.start; // Get the start time string

    // Convert the start time string to a Date object
    const startTime = new Date(startTimeTimestamp * 1000); // Convert seconds to milliseconds

    console.log('Start Time:', startTime.toISOString());
    // Calculate the duration in milliseconds
    const durationInMilliseconds = new Date() - startTime;

    // Convert duration to hours, minutes, and seconds
    const seconds = Math.floor((durationInMilliseconds / 1000) % 60).toString().padStart(2, '0');;
    const minutes = Math.floor((durationInMilliseconds / (1000 * 60)) % 60).toString().padStart(2, '0');;
    const hours = Math.floor((durationInMilliseconds / (1000 * 60 * 60))).toString().padStart(2, '0');
    
    // Use backticks for template literals
    const durationString = `${hours}:${minutes}:${seconds}`;
    
    console.log(durationString);
    return durationString;
  };
  const server_url = process.env.REACT_APP_CHARGING_STATION_SERVER_URL;
  const stopCharging = async () => {
    const response = await fetch('/api/stop'); 

    if (!response.ok) {
      throw new Error('Error in fetching CP status');
    }
    const result = await response.json();
    if (result.status === "Accepted"){

      setCPState("Summary")
      console.log("Setting summary", result)
      stopSession();
    }
  };

  const resetCharger = async () => {
    const response = await fetch('/api/reset'); 

    if (!response.ok) {
      throw new Error('Error in fetching CP status');
    }
    const result = await response.json();
    if (result.status === "Accepted"){
      setCPState("Ready");
    }
  };

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await fetch('/api/status'); 
        if (!response.ok) {
          throw new Error('Error in fetching CP status');
        }
        
        const result = await response.json();
        console.log("Setting CP State", result.station_status);
        
        if (result.station_status === "Charging") {
          console.log("Charging Session");
          startSession();
          var currentSessionInfo = {
            startTime: getDateReadable(result.session_status.start),
            duration: getDuration(result.session_status.start), 
            amountCharged: result.session_status.total_energy, 
            total_price: result.session_status.total_price, 
          };
          console.log("Updating session info:", currentSessionInfo);
          setSessionInfo(currentSessionInfo);
        }
    
        if (result.station_status === "Summary") {
          console.log("Stopping Session");
          stopSession();
        }
        setCPState(result.station_status);
        
      } catch (error) {
        console.error(error);
      }
    };

    //fetchStatus();  // Fetch CP state once when component mounts
    const intervalId = setInterval(fetchStatus, 1000);

    // Cleanup function to clear the interval when the component unmounts
    return () => clearInterval(intervalId);
  });

  useEffect(() => {
    if (CPState === "Ready") {
      const fetchQR = async () => {
        try {
          const response = await fetch('/api/qr'); 
          if (!response.ok) {
            throw new Error('Error in fetching QR data');
          }
          
          const result = await response.text();
          console.log("QR Data", result);
          setQRData(result.toString()); 
        } catch (error) {
          console.error(error);
        }
      };
      console.log("Fetching QR");
      fetchQR();
    }
    
  }, [CPState]); // Only run this effect when CPState changes

  return (
    <div className="App">
      <div className="page-container">

      <Header />
      
      
      <div className="carousel-container">
      <Carousel />
      </div>
    
      {(CPState === "Ready") && (
          
          <div className="charging-container">
          <div className="arrowBackground"></div>
              <div className="text-section">
                <div className="heading">

                      <TypeAnimation
                        sequence={[
                          
                          1000,
                          'Please', // First word appears
                          1000,
                        ]}
                        wrapper="div"
                        cursor={false}
                        repeat={Infinity}
                        style={{ display: 'block' }}
                        className="regular-text"
                      />

                      <TypeAnimation
                        sequence={[
                         
                          1000, // Wait for first word
                          'Scan', // Second word appears
                          1000,
                        ]}
                        wrapper="div"
                        cursor={false}
                        repeat={Infinity}
                        style={{ display: 'block' }}
                        className="green-text"
                      />

                      <TypeAnimation
                        sequence={[
                         
                          1000, // Wait for first two words
                          'To Start', // Third word appears
                          1000,
                        ]}
                        wrapper="div"
                        cursor={false}
                        repeat={Infinity}
                        style={{ display: 'block' }}
                        className="regular-text"
                      />

                </div>
              </div>
              <div className="qr-section">
                <QRCodeSVG value={QRdata} size={256} />
              </div>
          </div>
    

      )}

      {CPState === "Charging" && (

        <div className="session-container">
          <div className='text-section'>
            <div className='heading'>
              <div className='green-text' style={{ position: 'relative', zIndex: 1 }}>
                Charging
              </div>
              <div className='charging-icon'  style={{ position: 'relative' }}>
                <img src="icons/electricity.gif" style={{ width: '100%', height: '100%' }} />
              </div>
            </div>
          </div>
          <div className='session-section'>  
            {sessionInfo && ( // Conditional rendering
              <>
                <div className='session-row'>
                  <p className='label'>Start Time </p> 
                  <p className='value'>{sessionInfo.startTime}</p>
                </div>
                <div className='session-row'>
                  <p className='label'>Duration </p> 
                  <p className='value'>{sessionInfo.duration}</p>
                </div>
                <div className='session-row'>
                  <p className='label'>Amount Charged </p>
                  <p className='value'>{sessionInfo.amountCharged.toFixed(2)} kWh </p>
                  </div>  
                <div className='session-row'>
                  <p className='label'>Total Price </p>
                  <p className='value'>£ {sessionInfo.total_price.toFixed(2)}</p>
                </div>
              </>
            )}
            <button onClick={stopCharging} className="stop-button">Stop Charging</button>
              
          </div>
        </div>
      )}

      {CPState === "Summary" && (
        
        <div className="summary-container">
          <div className='text-section'>
            <div className='heading'>
              <div className='green-text'>
                Thank you
              </div>
              <div className='regular-text'>
                for using
              </div>
              <div className='regular-text'>
                our service!
              </div>
              <div className='regular-text'>
                  <Countdown
                  date={Date.now() + 10000}
                  intervalDelay={0}
                  onComplete={resetCharger}
                  renderer={props => <div>{props.seconds}</div>}
                  />
             </div>
            </div>
          </div>
          <div className='summary-section'>

            <div className='session-row'>
                  <p className='label'>Start Time </p> 
                  <p className='value'>{sessionSummary.startTime}</p>
                </div>
                <div className='session-row'>
                  <p className='label'>Duration </p> 
                  <p className='value'>{sessionSummary.duration}</p>
                </div>
                <div className='session-row'>
                  <p className='label'>Amount Charged </p>
                  <p className='value'>{sessionSummary.amountCharged.toFixed(2)} kWh </p>
                  </div>  
                <div className='session-row'>
                  <p className='label'>Total Price </p>
                  <p className='value'>{sessionSummary.total_price.toFixed(2)} £</p>
                </div>
            </div>
           
        </div>
      )}
    </div>
    </div>
  );
}

export default App;