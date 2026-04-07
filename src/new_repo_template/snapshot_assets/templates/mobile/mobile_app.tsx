import { StatusBar } from "expo-status-bar";
import { ScrollView, StyleSheet, Text, View } from "react-native";

import {
  NURT_FRONTEND_COPY,
  NURT_GETTING_STARTED_STEPS,
  NURT_WELCOME_HIGHLIGHTS,
} from "@generated/shared";

export default function App() {
  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <View style={styles.panel}>
        <Text style={styles.eyebrow}>{NURT_FRONTEND_COPY.eyebrow}</Text>
        <Text style={styles.title}>{NURT_FRONTEND_COPY.title}</Text>
        <Text style={styles.body}>{NURT_FRONTEND_COPY.body}</Text>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>{NURT_FRONTEND_COPY.highlightsHeading}</Text>
          {NURT_WELCOME_HIGHLIGHTS.map((highlight) => (
            <View key={highlight.title} style={styles.card}>
              <Text style={styles.cardTitle}>{highlight.title}</Text>
              <Text style={styles.cardBody}>{highlight.body}</Text>
            </View>
          ))}
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>{NURT_FRONTEND_COPY.gettingStartedHeading}</Text>
          {NURT_GETTING_STARTED_STEPS.map((step, index) => (
            <View key={step} style={styles.stepRow}>
              <View style={styles.stepIndex}>
                <Text style={styles.stepIndexText}>{index + 1}</Text>
              </View>
              <Text style={styles.stepText}>{step}</Text>
            </View>
          ))}
        </View>

        <View style={styles.actionRow}>
          <View style={styles.primaryAction}>
            <Text style={styles.primaryActionText}>{NURT_FRONTEND_COPY.primaryAction}</Text>
          </View>
          <View style={styles.secondaryAction}>
            <Text style={styles.secondaryActionText}>{NURT_FRONTEND_COPY.secondaryAction}</Text>
          </View>
        </View>

        <Text style={styles.footer}>{NURT_FRONTEND_COPY.caption}</Text>
      </View>
      <StatusBar style="auto" />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: "#071521",
  },
  content: {
    paddingHorizontal: 20,
    paddingVertical: 32,
  },
  panel: {
    gap: 18,
    borderRadius: 24,
    borderWidth: 1,
    borderColor: "#2e516e",
    backgroundColor: "#102538",
    padding: 20,
  },
  eyebrow: {
    color: "#78e7d5",
    fontSize: 13,
    fontWeight: "700",
    letterSpacing: 1.2,
    textTransform: "uppercase",
  },
  title: {
    color: "#eff8fb",
    fontSize: 30,
    fontWeight: "700",
  },
  body: {
    color: "#d5e8f1",
    fontSize: 16,
    lineHeight: 24,
  },
  section: {
    gap: 12,
  },
  sectionTitle: {
    color: "#eff8fb",
    fontSize: 20,
    fontWeight: "600",
  },
  card: {
    gap: 6,
    borderRadius: 18,
    backgroundColor: "#17314a",
    padding: 14,
  },
  cardTitle: {
    color: "#eff8fb",
    fontSize: 16,
    fontWeight: "600",
  },
  cardBody: {
    color: "#c3d9e6",
    fontSize: 14,
    lineHeight: 20,
  },
  stepRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 12,
  },
  stepIndex: {
    width: 28,
    height: 28,
    alignItems: "center",
    justifyContent: "center",
    borderRadius: 999,
    backgroundColor: "#78e7d5",
  },
  stepIndexText: {
    color: "#071521",
    fontWeight: "700",
  },
  stepText: {
    flex: 1,
    color: "#d5e8f1",
    fontSize: 14,
    lineHeight: 20,
  },
  actionRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 12,
  },
  primaryAction: {
    borderRadius: 999,
    backgroundColor: "#78e7d5",
    paddingHorizontal: 16,
    paddingVertical: 10,
  },
  secondaryAction: {
    borderRadius: 999,
    borderWidth: 1,
    borderColor: "#2e516e",
    backgroundColor: "#17314a",
    paddingHorizontal: 16,
    paddingVertical: 10,
  },
  primaryActionText: {
    color: "#071521",
    fontWeight: "700",
  },
  secondaryActionText: {
    color: "#eff8fb",
    fontWeight: "600",
  },
  footer: {
    color: "#a5c0d1",
    fontSize: 14,
    lineHeight: 20,
  },
});
