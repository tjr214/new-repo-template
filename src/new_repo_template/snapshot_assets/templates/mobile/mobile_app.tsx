import { StatusBar } from "expo-status-bar";
import { Text, View } from "react-native";

import { NURT_FRONTEND_COPY } from "@generated/shared";

export default function App() {
  return (
    <View style={{ flex: 1, alignItems: "center", justifyContent: "center" }}>
      <Text>{NURT_FRONTEND_COPY.title}</Text>
      <Text>{NURT_FRONTEND_COPY.body}</Text>
      <StatusBar style="auto" />
    </View>
  );
}
