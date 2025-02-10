import React, { useState, useEffect, useContext } from 'react';
import { View, Text, Button, StyleSheet } from 'react-native';
//import FastImage from 'react-native-fast-image';
import { Image } from 'expo-image';
import axios from 'axios';
import { UserContext } from '../UserContext';
import { get_start_api, get_status_api, get_stop_api } from '../config';


const ChargingScreen = ({ route, navigation }) => {
  const [isCharging, setIsCharging] = useState(false);
  const {username, setUsername, duration, setDuration, energyCharged, setEnergyCharged, total_price, setTotalPrice}= useContext(UserContext)
  const [CPState, setCPState] = useState(""); 
  const { startChargingAPI } = route.params.startChargingAPI;

  console.log(startChargingAPI);

  const getDuration = (startTimeTimestamp) => {
    //const startTimeString = result.session_status.start; // Get the start time string
    console.log("Start time", startTimeTimestamp);
    console.log("Start time",  new Date(startTimeTimestamp))
    const durationInMilliseconds = new Date() - new Date(startTimeTimestamp);

    // Convert duration to hours, minutes, and seconds
    const seconds = Math.floor((durationInMilliseconds / 1000) % 60);
    const minutes = Math.floor((durationInMilliseconds / (1000 * 60)) % 60);
    const hours = Math.floor((durationInMilliseconds / (1000 * 60 * 60)));
    const durationString = `${hours} hours, ${minutes} minutes, ${seconds} seconds`;
    
    console.log(durationString);
    return durationString;
  };
  

  const statusChargingAPI = get_status_api("CP_1");
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        console.log(statusChargingAPI);
        const response = await fetch(statusChargingAPI); 
        
        /*
        if (!response.ok) {
          throw new Error('Error in fetching CP status');
        }*/
        
        const result = await response.json();
        console.log("Setting CP State", result.cp_status);
        setCPState(result.cp_status);
        if (result.cp_status === "Charging"){
          console.log(new Date(result.session_status.start_time*1000));
          setDuration(getDuration(result.session_status.start_time));
          console.log("Setting Energy",result.session_status.total_energy);
          setEnergyCharged(result.session_status.total_energy);
          console.log("Setting Price",result.session_status.total_price);
          setTotalPrice(result.session_status.total_price);
        }
        if (result.cp_status === "Summary"){
          console.log("CP State", result.cp_status);
          navigateToSummary();
        }
        if (result.cp_status === "Inoperative"){
          console.log("CP State", result.cp_status);
          navigateToSummary();
        }
        
      } catch (error) {
        //console.error(error); // Log any errors
      }
    };
    fetchStatus();  // Fetch CP state once when component mounts
    const intervalId = setInterval(fetchStatus, 1000);

    return () => clearInterval(intervalId);
  }, []); 

  const navigateToSummary = () => {
      navigation.navigate('SummaryBilling', {
        duration,
        energyCharged,
        totalAmount: (energyCharged * 1).toFixed(2), // Assuming $1 per kWh
    });
  }
  
  const handleStartCharging = async () => {
    
    try {
      chargingAPI = startChargingAPI
      console.log('Attempting to call API:', chargingAPI);

      const response = await axios.get(get_start_api(chargingAPI, username, "ACME"));
      
      console.log('API response received:', response.data);
      
      if (response.data.status === "Accepted") {
        setIsCharging(true);
      }
    } catch (error) {
      if (axios.isAxiosError(error)) {
        console.log('Axios error:', error.message);
        if (error.response) {
          console.log('Error data:', error.response.data);
          console.log('Error status:', error.response.status);
        } else if (error.request) {
          console.log('Error request:', error.request);
        } else {
          console.log('Error', error.message);
        }
      } else {
        console.log('Unexpected error:', error);
      }
    }
  };

  const handleStopCharging = async () => {
    
    try {
        const response = await fetch(get_stop_api("CP_1"));
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const result = await response.json();
        if (result.status === "Accepted"){            
            setIsCharging(false);
            navigateToSummary();
        }
      } catch (error) {
      } finally {
      }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Charging Session</Text>
      {isCharging ? (
        <>
        <Image
            style={styles.gif}
            source={require('../assets/charging.gif')}
            contentFit="cover"
            transition={1000}
        />
          <Text style={styles.info}>Charging...</Text>
          <Text style={styles.info}>Duration: {duration}</Text>
          <Text style={styles.info}>Energy Charged: {(energyCharged*1).toFixed(2)} kWh</Text>
          <Text style={styles.info}>Total Price: {(total_price*1).toFixed(2)} GBP</Text>
          <Button title="Stop Charging" onPress={handleStopCharging} />
        </>
      ) : (
        <Button title="Start Charging" onPress={handleStartCharging} />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 16,
  },
  title: {
    fontSize: 24,
    marginBottom: 20,
  },
  gif: {
    width: 250,
    height: 250,
    marginBottom: 20,
  },
  info: {
    fontSize: 16,
    marginVertical: 5,
  },
});

export default ChargingScreen;