import { useMemo, useState } from "react";
import { StatusBar } from "expo-status-bar";
import {
  Pressable,
  StyleSheet,
  Text,
  TVEventHandlerEvent,
  useTVEventHandler,
  View,
} from "react-native";

const RAIL_ITEMS = ["Home", "Library", "Settings"] as const;

export default function App(): JSX.Element {
  const [focusedIndex, setFocusedIndex] = useState<number>(0);
  const [lastInputHint, setLastInputHint] = useState<string>("remote-primary");

  useTVEventHandler((event: TVEventHandlerEvent | undefined) => {
    const eventType = event?.eventType;
    if (eventType === undefined) {
      return;
    }

    if (
      eventType === "up" ||
      eventType === "down" ||
      eventType === "left" ||
      eventType === "right" ||
      eventType === "select" ||
      eventType === "playPause"
    ) {
      setLastInputHint("remote-primary");
      return;
    }

    setLastInputHint("keyboard/mouse/gamepad fallback");
  });

  const message = useMemo(() => {
    return `Focused item: ${RAIL_ITEMS[focusedIndex]} (${lastInputHint})`;
  }, [focusedIndex, lastInputHint]);

  return (
    <View style={styles.screen}>
      <Text style={styles.title}>Expo TV baseline</Text>
      <Text style={styles.subtitle}>{message}</Text>
      <View style={styles.rail}>
        {RAIL_ITEMS.map((item, index) => {
          const isFocused = index === focusedIndex;
          return (
            <Pressable
              key={item}
              hasTVPreferredFocus={index === 0}
              onFocus={() => setFocusedIndex(index)}
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
