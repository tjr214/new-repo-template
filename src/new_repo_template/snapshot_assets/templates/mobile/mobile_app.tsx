import { StatusBar } from "expo-status-bar";
import { ScrollView, StyleSheet, Text, View } from "react-native";

import {
  NURT_GETTING_STARTED_STEPS,
  NURT_WELCOME_ACTIONS,
  NURT_WELCOME_HERO,
  NURT_WELCOME_HIGHLIGHTS,
  NURT_WELCOME_SECTIONS,
} from "@generated/shared";

function MobileHeroPanel() {
  return (
    <View style={styles.heroPanel}>
      <View style={styles.heroHeader}>
        <Text style={styles.eyebrow}>{NURT_WELCOME_HERO.eyebrow}</Text>
        <View style={styles.heroLabelPill}>
          <Text style={styles.heroLabelText}>{NURT_WELCOME_HERO.label}</Text>
        </View>
      </View>
      <Text style={styles.title}>{NURT_WELCOME_HERO.title}</Text>
      <Text style={styles.body}>{NURT_WELCOME_HERO.body}</Text>
      <View style={styles.statusPill}>
        <View style={styles.statusDot} />
        <Text style={styles.statusText}>{NURT_WELCOME_HERO.status}</Text>
      </View>
    </View>
  );
}

function MobileHighlightCard({ highlight }: { highlight: (typeof NURT_WELCOME_HIGHLIGHTS)[number] }) {
  return (
    <View style={styles.card}>
      <Text style={styles.cardMeta}>{highlight.meta}</Text>
      <Text style={styles.cardTitle}>{highlight.title}</Text>
      <Text style={styles.cardBody}>{highlight.body}</Text>
    </View>
  );
}

function MobileStepCard({
  step,
  index,
}: {
  step: (typeof NURT_GETTING_STARTED_STEPS)[number];
  index: number;
}) {
  return (
    <View style={styles.stepCard}>
      <View style={styles.stepIndex}>
        <Text style={styles.stepIndexText}>{index + 1}</Text>
      </View>
      <View style={styles.stepCopyColumn}>
        <Text style={styles.stepTitle}>{step.title}</Text>
        <Text style={styles.stepText}>{step.body}</Text>
      </View>
    </View>
  );
}

function MobileActionRow() {
  return (
    <View style={styles.actionPanel}>
      <Text style={styles.sectionLabel}>Action Cluster</Text>
      <Text style={styles.sectionTitle}>{NURT_WELCOME_SECTIONS.actionsHeading}</Text>
      <View style={styles.actionRow}>
        <View style={styles.primaryAction}>
          <Text style={styles.primaryActionText}>{NURT_WELCOME_ACTIONS.primary}</Text>
        </View>
        <View style={styles.secondaryAction}>
          <Text style={styles.secondaryActionText}>{NURT_WELCOME_ACTIONS.secondary}</Text>
        </View>
      </View>
      <Text style={styles.footer}>{NURT_WELCOME_HERO.caption}</Text>
    </View>
  );
}

export default function App() {
  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <View style={styles.panel}>
        <MobileHeroPanel />

        <View style={styles.sectionPanel}>
          <Text style={styles.sectionLabel}>Shared Layer</Text>
          <Text style={styles.sectionTitle}>{NURT_WELCOME_SECTIONS.highlightsHeading}</Text>
          {NURT_WELCOME_HIGHLIGHTS.map((highlight) => (
            <MobileHighlightCard key={highlight.title} highlight={highlight} />
          ))}
        </View>

        <View style={styles.sectionPanel}>
          <Text style={styles.sectionLabel}>Execution Lane</Text>
          <Text style={styles.sectionTitle}>{NURT_WELCOME_SECTIONS.gettingStartedHeading}</Text>
          {NURT_GETTING_STARTED_STEPS.map((step, index) => (
            <MobileStepCard key={step.title} step={step} index={index} />
          ))}
        </View>

        <MobileActionRow />
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
  },
  heroPanel: {
    gap: 18,
    borderRadius: 24,
    borderWidth: 1,
    borderColor: "#2e516e",
    backgroundColor: "#102538",
    padding: 20,
  },
  heroHeader: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    gap: 12,
    flexWrap: "wrap",
  },
  eyebrow: {
    color: "#78e7d5",
    fontSize: 13,
    fontWeight: "700",
    letterSpacing: 1.2,
    textTransform: "uppercase",
  },
  heroLabelPill: {
    borderRadius: 999,
    borderWidth: 1,
    borderColor: "#2e516e",
    backgroundColor: "#17314a",
    paddingHorizontal: 12,
    paddingVertical: 6,
  },
  heroLabelText: {
    color: "#c6fff6",
    fontWeight: "700",
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
  statusPill: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    alignSelf: "flex-start",
    borderRadius: 999,
    borderWidth: 1,
    borderColor: "#2e516e",
    backgroundColor: "#17314a",
    paddingHorizontal: 12,
    paddingVertical: 8,
  },
  statusDot: {
    width: 10,
    height: 10,
    borderRadius: 999,
    backgroundColor: "#78e7d5",
  },
  statusText: {
    color: "#eff8fb",
    fontWeight: "600",
  },
  sectionPanel: {
    gap: 12,
    borderRadius: 22,
    borderWidth: 1,
    borderColor: "#2e516e",
    backgroundColor: "#102538",
    padding: 18,
  },
  sectionLabel: {
    color: "#a5c0d1",
    fontSize: 12,
    fontWeight: "700",
    letterSpacing: 1.1,
    textTransform: "uppercase",
  },
  sectionTitle: {
    color: "#eff8fb",
    fontSize: 20,
    fontWeight: "600",
  },
  card: {
    gap: 8,
    borderRadius: 18,
    backgroundColor: "#17314a",
    padding: 14,
  },
  cardMeta: {
    color: "#a5c0d1",
    fontSize: 12,
    fontWeight: "700",
    letterSpacing: 1,
    textTransform: "uppercase",
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
  stepCard: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 12,
    borderRadius: 18,
    backgroundColor: "#17314a",
    padding: 14,
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
  stepCopyColumn: {
    flex: 1,
    gap: 4,
  },
  stepTitle: {
    color: "#eff8fb",
    fontSize: 15,
    fontWeight: "600",
  },
  stepText: {
    color: "#d5e8f1",
    fontSize: 14,
    lineHeight: 20,
  },
  actionPanel: {
    gap: 12,
    borderRadius: 22,
    borderWidth: 1,
    borderColor: "#2e516e",
    backgroundColor: "#0d2030",
    padding: 18,
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
