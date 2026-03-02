import { StatusBar } from "expo-status-bar";
import { Text, View } from "react-native";

export default function App(): JSX.Element {
  return (
    <View style={{ flex: 1, alignItems: "center", justifyContent: "center" }}>
      <Text>Hello from Expo TV.</Text>
      <StatusBar style="auto" />
    </View>
  );
}
