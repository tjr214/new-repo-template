import { useState } from "react";
import { StatusBar } from "expo-status-bar";
import { Pressable, StyleSheet, Text, View } from "react-native";

import { NURT_FRONTEND_COPY, NURT_TV_WELCOME_CARDS } from "@generated/shared";

export default function App() {
  const [focusedIndex, setFocusedIndex] = useState<number>(0);
  const focusedCard = NURT_TV_WELCOME_CARDS[focusedIndex];
  const message = `Focused card: ${focusedCard.title} (remote-primary focus ready; keyboard/mouse/gamepad fallback supported)`;

  return (
    <View style={styles.screen}>
      <Text style={styles.eyebrow}>{NURT_FRONTEND_COPY.eyebrow}</Text>
      <Text style={styles.title}>{NURT_FRONTEND_COPY.title}</Text>
      <Text style={styles.copy}>{NURT_FRONTEND_COPY.body}</Text>
      <Text style={styles.subtitle}>{message}</Text>
      <View style={styles.layout}>
        <View style={styles.rail}>
          {NURT_TV_WELCOME_CARDS.map((card, index) => {
            const isFocused = index === focusedIndex;
            return (
              <Pressable
                key={card.title}
                hasTVPreferredFocus={index === 0}
                onFocus={() => setFocusedIndex(index)}
                onPress={() => setFocusedIndex(index)}
                style={[styles.item, isFocused ? styles.itemFocused : undefined]}
              >
                <Text style={styles.itemText}>{card.title}</Text>
              </Pressable>
            );
          })}
        </View>
        <View style={styles.detailPanel}>
          <Text style={styles.detailHeading}>{focusedCard.title}</Text>
          <Text style={styles.detailCopy}>{focusedCard.body}</Text>
          <Text style={styles.detailFooter}>{NURT_FRONTEND_COPY.caption}</Text>
        </View>
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
    paddingHorizontal: 32,
  },
  eyebrow: {
    color: "#78e7d5",
    fontSize: 18,
    fontWeight: "700",
    letterSpacing: 2,
    textTransform: "uppercase",
  },
  title: {
    color: "#d8f0ff",
    fontSize: 30,
    fontWeight: "700",
    textAlign: "center",
  },
  subtitle: {
    color: "#8bc2e6",
    fontSize: 18,
    textAlign: "center",
  },
  copy: {
    color: "#d8f0ff",
    fontSize: 16,
    maxWidth: 760,
    textAlign: "center",
  },
  layout: {
    width: "100%",
    maxWidth: 1100,
    flexDirection: "row",
    gap: 24,
    alignItems: "stretch",
    justifyContent: "center",
  },
  rail: {
    width: 360,
    gap: 12,
  },
  detailPanel: {
    flex: 1,
    maxWidth: 520,
    gap: 16,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: "#2e516e",
    backgroundColor: "#102538",
    paddingHorizontal: 24,
    paddingVertical: 22,
  },
  detailHeading: {
    color: "#eff8fb",
    fontSize: 28,
    fontWeight: "700",
  },
  detailCopy: {
    color: "#d8f0ff",
    fontSize: 18,
    lineHeight: 28,
  },
  detailFooter: {
    color: "#8bc2e6",
    fontSize: 16,
    lineHeight: 24,
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
