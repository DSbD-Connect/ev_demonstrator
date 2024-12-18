import React, { useState, useEffect, useContext } from "react";
import { StyleSheet, Text, TouchableOpacity, View , Button} from "react-native";
//import { BarCodeScanner } from 'expo-barcode-scanner';
import { CameraView, Camera } from "expo-camera";

import Ionicons from "react-native-vector-icons/Ionicons";

const QRCodeScanner = ({onSuccess}) => {
    const [hasPermission, setHasPermission] = useState(null);
    const [scanned, setScanned] = useState(false);

    useEffect(() => {
        const getCameraPermissions = async () => {
        const { status } = await Camera.requestCameraPermissionsAsync();
        setHasPermission(status === "granted");
        };

        getCameraPermissions();
    }, []);

    const handleBarcodeScanned = ({ type, data }) => {
        setScanned(true);
        alert(`Bar code with type ${type} and data ${data} has been scanned!`);
        console.log(data);
        onSuccess(data);

    };

    if (hasPermission === null) {
        return <Text>Requesting for camera permission</Text>;
    }
    if (hasPermission === false) {
        return <Text>No access to camera</Text>;
    }

    return (
        <View style={styles.container}>
        <CameraView
            barcodeScannerEnabled
            onBarcodeScanned={scanned ? undefined : handleBarcodeScanned}
            barcodeScannerSettings={{
            barcodeTypes: ["qr", "pdf417"],
            }}
            style={StyleSheet.absoluteFillObject}
        />
        {scanned && (
            <Button title={"Tap to Scan Again"} onPress={() => setScanned(false)} />
        )}
        </View>
    );
};

export default QRCodeScanner;

const styles = StyleSheet.create({
    container: {
      flex: 1,
      flexDirection: "column",
      justifyContent: "center",
    },
  });