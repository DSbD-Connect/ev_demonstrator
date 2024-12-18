import React, { createContext, useState } from 'react';

export const UserContext = createContext();

export const UserProvider = ({ children }) => {
    const [username, setUsername] = useState('');
    const [duration, setDuration] = useState(0); // in seconds
    const [energyCharged, setEnergyCharged] = useState(0); // in kWh
    const [total_price, setTotalPrice] = useState(0);
    const [cheri_on, setCheri] = useState(false);

    return (
        <UserContext.Provider 
        value={{ 
            username, 
            setUsername, 
            duration, 
            setDuration, 
            energyCharged, 
            setEnergyCharged,
            total_price,
            setTotalPrice,
            cheri_on,
            setCheri
        }}
    >
        {children}
    </UserContext.Provider>
    );
};