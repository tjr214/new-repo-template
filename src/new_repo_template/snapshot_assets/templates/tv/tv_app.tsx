import { useState } from "react";
import { StatusBar } from "expo-status-bar";
import { Pressable, StyleSheet, Text, View } from "react-native";

import { NURT_FRONTEND_COPY } from "@generated/shared";

const RAIL_ITEMS = ["Home", "Library", "Settings"] as const;

export default function App() {
  const [focusedIndex, setFocusedIndex] = useState<number>(0);
  const message = `Focused item: ${RAIL_ITEMS[focusedIndex]} (remote-primary focus ready; keyboard/mouse/gamepad fallback supported)`;

  return (
    <View style={styles.screen}>
      <Text style={styles.title}>{NURT_FRONTEND_COPY.title}</Text>
      <Text style={styles.copy}>{NURT_FRONTEND_COPY.body}</Text>
      <Text style={styles.subtitle}>{message}</Text>
      <View style={styles.rail}>
        {RAIL_ITEMS.map((item, index) => {
          const isFocused = index === focusedIndex;
          return (
            <Pressable
              key={item}
              hasTVPreferredFocus={index === 0}
              onFocus={() => setFocusedIndex(index)}
              onPress={() => setFocusedIndex(index)}
              style={[styles.item, isFocused ? styles.itemFocused : undefined]}
            >
              <Text style={styles.itemText}>{item}</Text>
            </Pressable>
          );
        })}
      </View>
      <StatusBar style="auto" />
    </View>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    gap: 20,
    backgroundColor: "#061a2b",
  },
  title: {
    color: "#d8f0ff",
    fontSize: 30,
    fontWeight: "700",
  },
  subtitle: {
    color: "#8bc2e6",
    fontSize: 18,
  },
  copy: {
    color: "#d8f0ff",
    fontSize: 16,
    maxWidth: 760,
    textAlign: "center",
  },
  rail: {
    width: 360,
    gap: 12,
  },
  item: {
    backgroundColor: "#17364f",
    borderColor: "transparent",
    borderWidth: 2,
    borderRadius: 12,
    paddingVertical: 16,
    paddingHorizontal: 20,
  },
  itemFocused: {
    borderColor: "#d8f0ff",
    transform: [{ scale: 1.04 }],
  },
  itemText: {
    color: "#ecf7ff",
    fontSize: 20,
    fontWeight: "600",
  },
});
