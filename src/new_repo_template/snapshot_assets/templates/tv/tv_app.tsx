import { useState } from "react";
import { StatusBar } from "expo-status-bar";
import { Pressable, StyleSheet, Text, View } from "react-native";

import {
  NURT_TV_WELCOME_CARDS,
  NURT_WELCOME_ACTIONS,
  NURT_WELCOME_HERO,
  NURT_WELCOME_SECTIONS,
} from "@generated/shared";

function TVFocusCard({
  card,
  index,
  isFocused,
  onFocus,
}: {
  card: (typeof NURT_TV_WELCOME_CARDS)[number];
  index: number;
  isFocused: boolean;
  onFocus: () => void;
}) {
  return (
    <Pressable
      key={card.title}
      hasTVPreferredFocus={index === 0}
      onFocus={onFocus}
      onPress={onFocus}
      style={[styles.item, isFocused ? styles.itemFocused : undefined]}
    >
      <Text style={styles.itemEyebrow}>{card.eyebrow}</Text>
      <Text style={styles.itemText}>{card.title}</Text>
    </Pressable>
  );
}

function TVFocusRail({
  focusedIndex,
  setFocusedIndex,
}: {
  focusedIndex: number;
  setFocusedIndex: (index: number) => void;
}) {
  return (
    <View style={styles.railPanel}>
      <Text style={styles.railHeading}>{NURT_WELCOME_SECTIONS.railHeading}</Text>
      <View style={styles.rail}>
        {NURT_TV_WELCOME_CARDS.map((card, index) => (
          <TVFocusCard
            key={card.title}
            card={card}
            index={index}
            isFocused={index === focusedIndex}
            onFocus={() => setFocusedIndex(index)}
          />
        ))}
      </View>
    </View>
  );
}

function TVDetailPanel({ card }: { card: (typeof NURT_TV_WELCOME_CARDS)[number] }) {
  return (
    <View style={styles.detailPanel}>
      <Text style={styles.detailLabel}>{card.eyebrow}</Text>
      <Text style={styles.detailHeading}>{card.title}</Text>
      <Text style={styles.detailCopy}>{card.body}</Text>
      <TVActionHint />
    </View>
  );
}

function TVActionHint() {
  return (
    <View style={styles.actionHintPanel}>
      <Text style={styles.actionHintLabel}>{NURT_WELCOME_SECTIONS.actionsHeading}</Text>
      <Text style={styles.actionHintText}>
        {NURT_WELCOME_ACTIONS.primary} or {NURT_WELCOME_ACTIONS.secondary}
      </Text>
      <Text style={styles.detailFooter}>{NURT_WELCOME_HERO.caption}</Text>
    </View>
  );
}

export default function App() {
  const [focusedIndex, setFocusedIndex] = useState<number>(0);
  const focusedCard = NURT_TV_WELCOME_CARDS[focusedIndex];
  const message = `Focused card: ${focusedCard.title} (remote-primary focus ready; keyboard/mouse/gamepad fallback supported)`;

  return (
    <View style={styles.screen}>
      <View style={styles.heroPanel}>
        <View style={styles.heroHeader}>
          <Text style={styles.eyebrow}>{NURT_WELCOME_HERO.eyebrow}</Text>
          <View style={styles.heroLabelPill}>
            <Text style={styles.heroLabelText}>{NURT_WELCOME_HERO.label}</Text>
          </View>
        </View>
        <Text style={styles.title}>{NURT_WELCOME_HERO.title}</Text>
        <Text style={styles.copy}>{NURT_WELCOME_HERO.body}</Text>
      </View>
      <Text style={styles.subtitle}>{message}</Text>
      <View style={styles.layout}>
        <TVFocusRail focusedIndex={focusedIndex} setFocusedIndex={setFocusedIndex} />
        <TVDetailPanel card={focusedCard} />
      </View>
      <StatusBar style="auto" />
    </View>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    alignItems: "center",
    gap: 20,
    backgroundColor: "#061a2b",
    paddingHorizontal: 32,
    paddingVertical: 28,
  },
  heroPanel: {
    width: "100%",
    maxWidth: 1100,
    gap: 14,
    borderRadius: 24,
    borderWidth: 1,
    borderColor: "#2e516e",
    backgroundColor: "#102538",
    paddingHorizontal: 24,
    paddingVertical: 20,
  },
  heroHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    gap: 16,
  },
  heroLabelPill: {
    borderRadius: 999,
    borderWidth: 1,
    borderColor: "#2e516e",
    backgroundColor: "#17364f",
    paddingHorizontal: 14,
    paddingVertical: 8,
  },
  heroLabelText: {
    color: "#c6fff6",
    fontSize: 16,
    fontWeight: "700",
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
    fontSize: 34,
    fontWeight: "700",
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
  railPanel: {
    width: 360,
    gap: 14,
  },
  railHeading: {
    color: "#a5c0d1",
    fontSize: 16,
    fontWeight: "700",
    letterSpacing: 1.2,
    textTransform: "uppercase",
  },
  rail: {
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
  detailLabel: {
    color: "#a5c0d1",
    fontSize: 16,
    fontWeight: "700",
    letterSpacing: 1.2,
    textTransform: "uppercase",
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
  actionHintPanel: {
    gap: 10,
    marginTop: 12,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: "#2e516e",
    backgroundColor: "#17364f",
    paddingHorizontal: 18,
    paddingVertical: 16,
  },
  actionHintLabel: {
    color: "#a5c0d1",
    fontSize: 14,
    fontWeight: "700",
    letterSpacing: 1,
    textTransform: "uppercase",
  },
  actionHintText: {
    color: "#eff8fb",
    fontSize: 18,
    fontWeight: "600",
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
    borderRadius: 18,
    paddingVertical: 16,
    paddingHorizontal: 20,
    gap: 8,
  },
  itemFocused: {
    borderColor: "#d8f0ff",
    transform: [{ scale: 1.04 }],
  },
  itemEyebrow: {
    color: "#a5c0d1",
    fontSize: 14,
    fontWeight: "700",
    letterSpacing: 1,
    textTransform: "uppercase",
  },
  itemText: {
    color: "#ecf7ff",
    fontSize: 20,
    fontWeight: "600",
  },
});
