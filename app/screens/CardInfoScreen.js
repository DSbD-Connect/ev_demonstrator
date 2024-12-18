import React, { useState, useContext } from 'react';
import { View, TextInput, Button, StyleSheet, Text } from 'react-native';
import { get_card_provider_api, get_login_api } from '../config';
import { UserContext } from '../UserContext';

const CardInfoScreen = ({ route, navigation }) => {
  const [cardNumber, setCardNumber] = useState('');
  const [expiryDate, setExpiryDate] = useState('');
  const [cvv, setCvv] = useState('');
  const {cheri_on} =  useContext(UserContext);
  const [cardProvider, setCardProvider] = useState('');

  console.log(route.params);

  const fetchCardProvider = async () => {
    try {
      const settings = {
        method: 'POST',
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          "credit_card_number": cardNumber.toString(),
          "expiry_date": "10/20",
          "cvv":"111",
          "amount": "0", // placeholder
          "cheri_on": cheri_on,
        }),
      };
      console.log(settings);
      const response = await fetch(get_card_provider_api(), settings);
      const data = await response.text();
      console.log('Card Provider Data:', data);
      setCardProvider(data || 'Unknown Provider'); // Update state with the API result
    } catch (error) {
      console.error("Error fetching card provider:", error);
      console.log(data);
      setCardProvider('Error fetching provider');
    }
  };

  const handleSubmit = () => {
    // Implement card info submission logic here
    console.log('Card info submitted');
    navigation.navigate('Charging', {startChargingAPI: route.params}); // Navigate to Charging Screen
  };

  const handleCardNumberChange = (number) => {
    setCardNumber(number);
    
    // Check if the number has at least 4 characters
    if (number.length === 4) {
      fetchCardProvider(number); // Call the API with the first four digits
    }
  };
  
  return (
    <View style={styles.container}>
      <TextInput 
        style={styles.input}
        placeholder="Card Number"
        value={cardNumber}
        onChangeText={handleCardNumberChange}
      />
      <TextInput 
        style={styles.input}
        placeholder="Expiry Date (MM/YY)"
        value={expiryDate}
        onChangeText={setExpiryDate}
      />
      <TextInput 
        style={styles.input}
        placeholder="CVV"
        secureTextEntry
        value={cvv}
        onChangeText={setCvv}
      />
      <Button title="Submit" onPress={handleSubmit} />

      <Text style={styles.resultLabel}>Card Provider:</Text>
      <TextInput 
        style={[styles.resultInput, { height: Math.max(100, cardProvider.length * 10) }]}
        value={cardProvider}
        multiline={true}
        editable={false} 
        numberOfLines={25} // Optional: set a reasonable default height

      />

    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    padding: 16,
  },
  input: {
    height: 40,
    borderColor: 'gray',
    borderWidth: 1,
    marginBottom: 12,
    paddingHorizontal: 8,
  },
  resultLabel: {
    marginTop: 20,
    fontSize: 18,
    fontWeight: 'bold',
  },
  resultInput: {
    height: 40,
    borderColor: 'gray',
    borderWidth: 1,
    paddingVertical:10,
    paddingHorizontal: 8,
    minHeight: 40, // Minimum height for the input field
    maxHeight:400,
    backgroundColor: '#f0f0f0', // Change background for visibility
  },
});

export default CardInfoScreen;