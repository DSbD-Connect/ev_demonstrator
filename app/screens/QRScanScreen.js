import React from 'react';
import { View, Text, Button, StyleSheet } from 'react-native';
//import { RNCamera } from 'react-native-camera';
//import QRCodeScanner from 'react-native-qrcode-scanner';
//import QRScanner from '../screens/QRScanner.js';
import QRCodeScanner from './QRCodeScanner.js';

const QRScanScreen = ({ navigation }) => {
  const onSuccess = (e) => {
    if (e != null){
      console.log('QR Code scanned:', e);
      navigation.navigate('CardInfo', {startChargingAPI: e}); // Navigate to Card Info after scanning
    }else{
      navigation.navigate('Welcome'); // Navigate to Card Info after scanning
    }
    
  };

  return (
    <View style={styles.container}>
      <QRCodeScanner onSuccess={onSuccess}
        topContent={<Text style={styles.instructions}>Scan your QR code to start charging</Text>}
        bottomContent={<Button title="Cancel" onPress={() => navigation.navigate('Login')} />}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
  },
  instructions: {
    fontSize: 18,
    margin: 32,
    textAlign: 'center',
  },
});

export default QRScanScreen;