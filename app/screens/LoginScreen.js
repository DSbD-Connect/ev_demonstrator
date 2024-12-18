import React, { useState, useContext } from 'react';
import { View, TextInput, Button, StyleSheet, Switch, Text } from 'react-native';
import { get_login_api } from '../config';
import { UserContext } from '../UserContext'; 

const LoginScreen = ({ navigation }) => {
  const { setUsername, cheri_on, setCheri } = useContext(UserContext); // Access the setUsername function from context
  const [username, setUsernameState] = useState(''); // Local state for input
  const [password, setPassword] = useState('');
  const [isEnabled, setIsEnabled] = useState(false);
  
  //const toggleSwitch = () => setIsEnabled(previousState => !previousState);
  const toggleSwitch = () => setCheri(previousState => !previousState);

  const handleLogin = () => {
    const login = async () => {
      try {
        const settings = {
          method: 'POST',
          headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            username,
            password,
            cheri_on: isEnabled,
          }),
        };
        
        const response = await fetch(get_login_api(), settings); 
        if (!response.ok) {
          throw new Error('Error in login');
        }
        
        const result = await response.json();
        setUsername(username); // Set the username in context
        navigation.navigate('Welcome');
      } catch (error) {
        console.error(error);
      }
    };
    login();  
  };

  return (
    <View style={styles.container}>
      <TextInput 
        style={styles.input}
        placeholder="Username"
        value={username}
        onChangeText={setUsernameState} // Update local state
      />
      <TextInput 
        style={styles.input}
        placeholder="Password"
        secureTextEntry
        value={password}
        onChangeText={setPassword}
      />
      <View style={styles.switchContainer}>
        <Text>Enable CHERI:</Text>
        <Switch
          trackColor={{ false: '#767577', true: '#81b0ff' }}
          thumbColor={isEnabled ? '#f5dd4b' : '#f4f3f4'}
          ios_backgroundColor="#3e3e3e"
          onValueChange={toggleSwitch}
          value={cheri_on}
        />
      </View>
      <Button title="Login" onPress={handleLogin} />
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
  switchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
});

export default LoginScreen;