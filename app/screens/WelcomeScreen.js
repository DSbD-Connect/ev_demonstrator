import React from 'react';
import { View, Text, Button, StyleSheet } from 'react-native';

const WelcomeScreen = ({ navigation }) => {
  const handleStartScan = () => {
    navigation.navigate('QRScan'); // Navigate to QR Scan
  };

  return (
    <View style={styles.container}>
      <Text style={styles.welcomeText}>Welcome to the EV Charging App!</Text>
      <Text style={styles.instructions}>Scan a QR code to start charging your vehicle.</Text>
      <Button title="Start QR Scan" onPress={handleStartScan} style={styles.button} />
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
  welcomeText: {
    fontSize: 24,
    marginBottom: 20,
    textAlign: 'center',
  },
  instructions: {
    fontSize: 16,
    marginBottom: 40,
    textAlign: 'center',
  },
  button: {
    marginTop: 20,
  },
});

export default WelcomeScreen;