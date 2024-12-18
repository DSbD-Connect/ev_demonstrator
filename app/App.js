import { registerRootComponent } from "expo";


import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import LoginScreen from './screens/LoginScreen.js';
import WelcomeScreen from './screens/WelcomeScreen';
import QRScanScreen from './screens/QRScanScreen';
import CardInfoScreen from './screens/CardInfoScreen';
import ChargingScreen from './screens/ChargingScreen';
import SummaryBillingScreen from './screens/SummaryBillingScreen';
import { UserProvider } from './UserContext';

const Stack = createNativeStackNavigator();

export default function App() {
  return (
    <UserProvider>
      <NavigationContainer>
        <Stack.Navigator initialRouteName="Login">
        <Stack.Screen name="Login" component={LoginScreen} />
        <Stack.Screen name="Welcome" component={WelcomeScreen} />
        <Stack.Screen name="QRScan" component={QRScanScreen} />
        <Stack.Screen name="CardInfo" component={CardInfoScreen} />
        <Stack.Screen name="Charging" component={ChargingScreen} />
        <Stack.Screen name="SummaryBilling" component={SummaryBillingScreen} />
        
        </Stack.Navigator>
      </NavigationContainer>
    </UserProvider>
  );
}

registerRootComponent(App);