import { useEffect, useState } from "react";
import QRCode from "react-native-qrcode-svg";
import { StatusBar } from "expo-status-bar";
import { Pressable, StyleSheet, Text, View } from "react-native";

import { NURT_WELCOME_HERO } from "@generated/shared";

type DeviceLinkPollingState =
  | "authorization_pending"
  | "slow_down"
  | "access_denied"
  | "expired_token"
  | "invalid_grant"
  | "invalid_request"
  | "linked";

interface DeviceLinkSessionResponse {
  device_code: string;
  user_code: string;
  verification_uri: string;
  verification_uri_complete: string;
  expires_in: number;
  interval: number;
}

const DEFAULT_VERIFICATION_URI =
  process.env.EXPO_PUBLIC_DEVICE_LINK_BASE_URL ?? "http://localhost:3000/device";
const DEFAULT_EXPIRES_IN_SECONDS = Number(
  process.env.EXPO_PUBLIC_DEVICE_LINK_EXPIRES_IN_SECONDS ?? "600"
);
const DEFAULT_POLL_INTERVAL_SECONDS = Number(
  process.env.EXPO_PUBLIC_DEVICE_LINK_POLL_INTERVAL_SECONDS ?? "5"
);
const AUTO_LINK_DEMO = process.env.EXPO_PUBLIC_DEVICE_LINK_DEMO_AUTO_LINK === "true";

function createDeviceLinkSession(revision: number): DeviceLinkSessionResponse {
  const serial = String(1400 + revision).padStart(4, "0");
  const user_code = `NURT-${serial}`;
  const verification_uri = DEFAULT_VERIFICATION_URI;
  const verification_uri_complete = `${verification_uri}?user_code=${encodeURIComponent(user_code)}`;

  return {
    device_code: `tv-device-${serial}`,
    user_code,
    verification_uri,
    verification_uri_complete,
    expires_in: DEFAULT_EXPIRES_IN_SECONDS,
    interval: DEFAULT_POLL_INTERVAL_SECONDS,
  };
}

function statusCopyForState(state: DeviceLinkPollingState): string {
  switch (state) {
    case "authorization_pending":
      return "Waiting for the signed-in web user to approve this TV.";
    case "slow_down":
      return "Polling too quickly. Back off before checking again.";
    case "access_denied":
      return "The web user denied this TV request.";
    case "expired_token":
      return "This code expired. Refresh to issue a new link request.";
    case "invalid_grant":
      return "The backend rejected this device code. Issue a fresh link request.";
    case "invalid_request":
      return "The polling payload is invalid. Fix the device-link request contract.";
    case "linked":
      return "Link complete. Replace the starter state with your signed-in TV surface.";
  }
}

function statusLabelForState(state: DeviceLinkPollingState): string {
  switch (state) {
    case "authorization_pending":
      return "authorization_pending";
    case "slow_down":
      return "slow_down";
    case "access_denied":
      return "access_denied";
    case "expired_token":
      return "expired_token";
    case "invalid_grant":
      return "invalid_grant";
    case "invalid_request":
      return "invalid_request";
    case "linked":
      return "linked";
  }
}

function PairingStatusChip({ state }: { state: DeviceLinkPollingState }) {
  return (
    <View style={styles.statusChip}>
      <Text style={styles.statusChipLabel}>{statusLabelForState(state)}</Text>
    </View>
  );
}

function SignedInPanel({ token }: { token: string }) {
  return (
    <View style={styles.linkedPanel}>
      <Text style={styles.linkedEyebrow}>{NURT_WELCOME_HERO.label}</Text>
      <Text style={styles.linkedTitle}>TV Session Ready</Text>
      <Text style={styles.linkedBody}>{NURT_WELCOME_HERO.title}</Text>
      <Text style={styles.linkedFooter}>App session token: {token}</Text>
    </View>
  );
}

export default function App() {
  const [sessionRevision, setSessionRevision] = useState(0);
  const [pollState, setPollState] = useState<DeviceLinkPollingState>(
    "authorization_pending"
  );
  const [secondsRemaining, setSecondsRemaining] = useState(DEFAULT_EXPIRES_IN_SECONDS);
  const [linkedToken, setLinkedToken] = useState<string | null>(null);
  const session = createDeviceLinkSession(sessionRevision);

  useEffect(() => {
    setPollState("authorization_pending");
    setLinkedToken(null);
    setSecondsRemaining(session.expires_in);
  }, [session.device_code, session.expires_in]);

  useEffect(() => {
    if (pollState === "expired_token" || pollState === "linked") {
      return;
    }

    const timer = setInterval(() => {
      setSecondsRemaining((current) => {
        if (current <= 1) {
          setPollState("expired_token");
          return 0;
        }
        return current - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [pollState]);

  useEffect(() => {
    if (!AUTO_LINK_DEMO || pollState !== "authorization_pending") {
      return;
    }

    const timer = setTimeout(() => {
      setPollState("linked");
      setLinkedToken(`tv-session-${session.device_code}`);
    }, session.interval * 3000);

    return () => clearTimeout(timer);
  }, [pollState, session.device_code, session.interval]);

  return (
    <View style={styles.screen}>
      <View style={styles.pairingCard}>
        <View style={styles.headerRow}>
          <Text style={styles.eyebrow}>TV Device Link</Text>
          <PairingStatusChip state={pollState} />
        </View>
        <Text style={styles.title}>Verify on your phone</Text>
        <Text style={styles.body}>
          Scan the QR code or visit the fallback URL, sign in on the web, and approve
          this TV against the backend-owned device-link record.
        </Text>
        <View style={styles.qrPanel}>
          <QRCode size={280} value={session.verification_uri_complete} />
        </View>
        <View style={styles.instructionsPanel}>
          <Text style={styles.instructionsLabel}>verification_uri_complete</Text>
          <Text style={styles.instructionsValue}>{session.verification_uri_complete}</Text>
          <Text style={styles.instructionsLabel}>verification_uri</Text>
          <Text style={styles.instructionsValue}>{session.verification_uri}</Text>
          <Text style={styles.instructionsLabel}>user_code</Text>
          <Text style={styles.codeValue}>{session.user_code}</Text>
        </View>
        <View style={styles.footerRow}>
          <View style={styles.statusPanel}>
            <Text style={styles.statusHeading}>Polling State</Text>
            <Text style={styles.statusCopy}>{statusCopyForState(pollState)}</Text>
            <Text style={styles.statusMeta}>Expires in {secondsRemaining}s</Text>
            <Text style={styles.statusMeta}>Poll interval {session.interval}s</Text>
          </View>
          <Pressable
            hasTVPreferredFocus
            onPress={() => setSessionRevision((current) => current + 1)}
            style={({ focused, pressed }) => [
              styles.refreshButton,
              focused ? styles.refreshButtonFocused : undefined,
              pressed ? styles.refreshButtonPressed : undefined,
            ]}
          >
            <Text style={styles.refreshButtonText}>Refresh code</Text>
          </Pressable>
        </View>
      </View>
      {linkedToken ? <SignedInPanel token={linkedToken} /> : null}
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
    paddingVertical: 28,
  },
  pairingCard: {
    width: "100%",
    maxWidth: 980,
    gap: 18,
    borderRadius: 24,
    borderWidth: 1,
    borderColor: "#2e516e",
    backgroundColor: "#102538",
    paddingHorizontal: 28,
    paddingVertical: 24,
  },
  headerRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    gap: 16,
  },
  eyebrow: {
    color: "#78e7d5",
    fontSize: 18,
    fontWeight: "700",
    letterSpacing: 2,
    textTransform: "uppercase",
  },
  statusChip: {
    borderRadius: 999,
    borderWidth: 1,
    borderColor: "#2e516e",
    backgroundColor: "#17364f",
    paddingHorizontal: 14,
    paddingVertical: 8,
  },
  statusChipLabel: {
    color: "#c6fff6",
    fontSize: 16,
    fontWeight: "700",
  },
  title: {
    color: "#d8f0ff",
    fontSize: 34,
    fontWeight: "700",
    textAlign: "center",
  },
  body: {
    color: "#d8f0ff",
    fontSize: 18,
    lineHeight: 28,
    textAlign: "center",
  },
  qrPanel: {
    alignSelf: "center",
    borderRadius: 20,
    backgroundColor: "#f4fbff",
    padding: 20,
  },
  instructionsPanel: {
    gap: 8,
    borderRadius: 18,
    borderWidth: 1,
    borderColor: "#2e516e",
    backgroundColor: "#17364f",
    paddingHorizontal: 18,
    paddingVertical: 16,
  },
  instructionsLabel: {
    color: "#a5c0d1",
    fontSize: 14,
    fontWeight: "700",
    letterSpacing: 1,
    textTransform: "uppercase",
  },
  instructionsValue: {
    color: "#eff8fb",
    fontSize: 18,
  },
  codeValue: {
    color: "#eff8fb",
    fontSize: 28,
    fontWeight: "700",
    letterSpacing: 4,
  },
  footerRow: {
    flexDirection: "row",
    alignItems: "stretch",
    justifyContent: "space-between",
    gap: 20,
  },
  statusPanel: {
    flex: 1,
    gap: 8,
  },
  statusHeading: {
    color: "#a5c0d1",
    fontSize: 14,
    fontWeight: "700",
    letterSpacing: 1,
    textTransform: "uppercase",
  },
  statusCopy: {
    color: "#eff8fb",
    fontSize: 18,
    lineHeight: 26,
  },
  statusMeta: {
    color: "#8bc2e6",
    fontSize: 16,
  },
  refreshButton: {
    alignItems: "center",
    justifyContent: "center",
    minWidth: 220,
    borderRadius: 18,
    borderWidth: 2,
    borderColor: "transparent",
    backgroundColor: "#17364f",
    paddingHorizontal: 20,
    paddingVertical: 18,
  },
  refreshButtonFocused: {
    borderColor: "#d8f0ff",
    transform: [{ scale: 1.03 }],
  },
  refreshButtonPressed: {
    opacity: 0.9,
  },
  refreshButtonText: {
    color: "#ecf7ff",
    fontSize: 20,
    fontWeight: "700",
  },
  linkedPanel: {
    width: "100%",
    maxWidth: 980,
    gap: 12,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: "#2e516e",
    backgroundColor: "#17364f",
    paddingHorizontal: 24,
    paddingVertical: 20,
  },
  linkedEyebrow: {
    color: "#a5c0d1",
    fontSize: 14,
    fontWeight: "700",
    letterSpacing: 1,
    textTransform: "uppercase",
  },
  linkedTitle: {
    color: "#eff8fb",
    fontSize: 28,
    fontWeight: "700",
  },
  linkedBody: {
    color: "#d8f0ff",
    fontSize: 18,
    lineHeight: 28,
  },
  linkedFooter: {
    color: "#8bc2e6",
    fontSize: 16,
  },
});
