import React, {useContext } from 'react';
import { View, Text, Button, StyleSheet } from 'react-native';
import { UserContext } from '../UserContext';

const SummaryBillingScreen = ({ navigation }) => {
  const {username, setUsername, duration, setDuration, energyCharged, setEnergyCharged, total_price, setTotalPrice}= useContext(UserContext);

  const handlePayment = () => {
    // Implement payment submission logic here
    console.log('Payment confirmed');
    // Navigate to a confirmation screen or back to the login
    navigation.navigate('Login'); // Example navigation
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Charging Summary & Billing</Text>
      <Text style={styles.info}>Session Duration: {duration}</Text>
      <Text style={styles.info}>Amount Charged: {energyCharged.toFixed(2)} kWh</Text>
      <Text style={styles.info}>Total Amount: {total_price.toFixed(2)}</Text>
      <Text style={styles.info}>Payment Method: Credit Card</Text>
      <Button title="Confirm Payment" onPress={handlePayment} />
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
  info: {
    fontSize: 16,
    marginVertical: 5,
  },
});

export default SummaryBillingScreen;