import Storage from "expo-sqlite/kv-store";
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
  client_id: string;
  user_code: string;
  verification_uri: string;
  verification_uri_complete: string;
  expires_in: number;
  interval: number;
}

interface TvAppSession {
  accessToken: string;
  deviceCode: string;
  userId: string;
  expiresAtMs: number;
}

interface TvAppSessionResponse {
  authenticated: boolean;
  user_id: string;
  expires_in: number;
}

interface DeviceLinkErrorResponse {
  error: DeviceLinkPollingState;
  error_description: string;
}

const DEFAULT_VERIFICATION_URI =
  process.env.EXPO_PUBLIC_DEVICE_LINK_BASE_URL ?? "http://localhost:3000/device";
const DEFAULT_DEVICE_LINK_API_URL =
  process.env.EXPO_PUBLIC_DEVICE_LINK_API_URL ?? "http://127.0.0.1:3210";
const DEFAULT_EXPIRES_IN_SECONDS = Number(
  process.env.EXPO_PUBLIC_DEVICE_LINK_EXPIRES_IN_SECONDS ?? "600"
);
const DEFAULT_POLL_INTERVAL_SECONDS = Number(
  process.env.EXPO_PUBLIC_DEVICE_LINK_POLL_INTERVAL_SECONDS ?? "5"
);
const AUTO_LINK_DEMO = process.env.EXPO_PUBLIC_DEVICE_LINK_DEMO_AUTO_LINK === "true";
const DEVICE_LINK_CLIENT_ID = process.env.EXPO_PUBLIC_DEVICE_LINK_CLIENT_ID ?? "generated-tv";
const TV_APP_SESSION_STORAGE_KEY = "nurt.tv.app-session";

function createDeviceLinkSession(revision: number): DeviceLinkSessionResponse {
  const serial = String(1400 + revision).padStart(4, "0");
  const user_code = `NURT-${serial}`;
  const verification_uri = DEFAULT_VERIFICATION_URI;
  const verification_uri_complete = `${verification_uri}?user_code=${encodeURIComponent(user_code)}`;

  return {
    device_code: `tv-device-${serial}`,
    client_id: DEVICE_LINK_CLIENT_ID,
    user_code,
    verification_uri,
    verification_uri_complete,
    expires_in: DEFAULT_EXPIRES_IN_SECONDS,
    interval: DEFAULT_POLL_INTERVAL_SECONDS,
  };
}

async function issueLiveDeviceLinkSession(): Promise<DeviceLinkSessionResponse> {
  if (AUTO_LINK_DEMO) {
    return createDeviceLinkSession(0);
  }

  const response = await fetch(`${DEFAULT_DEVICE_LINK_API_URL}/device/code`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ client_id: DEVICE_LINK_CLIENT_ID }),
  });

  if (!response.ok) {
    throw new Error("Failed to create device-link session.");
  }

  const payload = (await response.json()) as DeviceLinkSessionResponse;
  return {
    ...payload,
    client_id: payload.client_id ?? DEVICE_LINK_CLIENT_ID,
  };
}

async function persistTvAppSession(session: TvAppSession | null) {
  if (session === null) {
    await Storage.removeItem(TV_APP_SESSION_STORAGE_KEY);
    return;
  }
  await Storage.setItem(TV_APP_SESSION_STORAGE_KEY, JSON.stringify(session));
}

async function readPersistedTvAppSession(): Promise<TvAppSession | null> {
  const rawSession = await Storage.getItem(TV_APP_SESSION_STORAGE_KEY);
  if (!rawSession) {
    return null;
  }
  return JSON.parse(rawSession) as TvAppSession;
}

async function validatePersistedTvSession(
  session: TvAppSession
): Promise<TvAppSessionResponse | null> {
  const response = await fetch(`${DEFAULT_DEVICE_LINK_API_URL}/device/session`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ access_token: session.accessToken }),
  });

  if (!response.ok) {
    return null;
  }

  return (await response.json()) as TvAppSessionResponse;
}

async function revokePersistedTvSession(session: TvAppSession | null) {
  if (!session || AUTO_LINK_DEMO) {
    await persistTvAppSession(null);
    return;
  }

  await fetch(`${DEFAULT_DEVICE_LINK_API_URL}/device/logout`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ access_token: session.accessToken }),
  });

  await persistTvAppSession(null);
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
  const [deviceSession, setDeviceSession] = useState<DeviceLinkSessionResponse | null>(null);
  const [pollState, setPollState] = useState<DeviceLinkPollingState>(
    "authorization_pending"
  );
  const [secondsRemaining, setSecondsRemaining] = useState(DEFAULT_EXPIRES_IN_SECONDS);
  const [linkedSession, setLinkedSession] = useState<TvAppSession | null>(null);
  const [restoreMessage, setRestoreMessage] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function restoreOrIssueSession() {
      const persistedSession = await readPersistedTvAppSession();
      if (persistedSession) {
        const validatedSession = await validatePersistedTvSession(persistedSession);
        if (!cancelled && validatedSession?.authenticated) {
          setLinkedSession(persistedSession);
          setRestoreMessage("Restored TV app session from local storage.");
          return;
        }
        await persistTvAppSession(null);
      }

      try {
        const nextSession = AUTO_LINK_DEMO
          ? createDeviceLinkSession(sessionRevision)
          : await issueLiveDeviceLinkSession();
        if (cancelled) {
          return;
        }
        setDeviceSession(nextSession);
        setPollState("authorization_pending");
        setLinkedSession(null);
        setSecondsRemaining(nextSession.expires_in);
        setRestoreMessage(null);
      } catch (error) {
        if (!cancelled) {
          setPollState("invalid_request");
          setRestoreMessage(
            error instanceof Error ? error.message : "Failed to issue a device-link session."
          );
        }
      }
    }

    void restoreOrIssueSession();

    return () => {
      cancelled = true;
    };
  }, [sessionRevision]);

  useEffect(() => {
    if (!deviceSession || pollState === "expired_token" || linkedSession) {
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
  }, [deviceSession, linkedSession, pollState]);

  useEffect(() => {
    if (!deviceSession || pollState === "expired_token" || linkedSession) {
      return;
    }

    const timer = setTimeout(() => {
      void (async () => {
        if (AUTO_LINK_DEMO) {
          const demoSession = {
            accessToken: `tv-session-${deviceSession.device_code}`,
            deviceCode: deviceSession.device_code,
            userId: "demo-user",
            expiresAtMs: Date.now() + deviceSession.expires_in * 1000,
          } satisfies TvAppSession;
          setPollState("linked");
          setLinkedSession(demoSession);
          await persistTvAppSession(demoSession);
          return;
        }

        const response = await fetch(`${DEFAULT_DEVICE_LINK_API_URL}/device/token`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            client_id: deviceSession.client_id,
            device_code: deviceSession.device_code,
            grant_type: "urn:ietf:params:oauth:grant-type:device_code",
          }),
        });

        if (response.ok) {
          const payload = (await response.json()) as {
            access_token: string;
            expires_in: number;
            user_id?: string;
          };
          const nextSession = {
            accessToken: payload.access_token,
            deviceCode: deviceSession.device_code,
            userId: payload.user_id ?? "approved-user",
            expiresAtMs: Date.now() + payload.expires_in * 1000,
          } satisfies TvAppSession;
          setPollState("linked");
          setLinkedSession(nextSession);
          await persistTvAppSession(nextSession);
          return;
        }

        const error = (await response.json()) as DeviceLinkErrorResponse;
        setPollState(error.error);
      })();
    }, deviceSession.interval * 1000);

    return () => clearTimeout(timer);
  }, [AUTO_LINK_DEMO, deviceSession, linkedSession, pollState]);

  async function handleRefreshCode() {
    await revokePersistedTvSession(linkedSession);
    setSessionRevision((current) => current + 1);
  }

  async function handleLogout() {
    await revokePersistedTvSession(linkedSession);
    setLinkedSession(null);
    setSessionRevision((current) => current + 1);
  }

  const activeSession = deviceSession;

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
        {activeSession ? (
          <>
            <View style={styles.qrPanel}>
              <QRCode size={280} value={activeSession.verification_uri_complete} />
            </View>
            <View style={styles.instructionsPanel}>
              <Text style={styles.instructionsLabel}>verification_uri_complete</Text>
              <Text style={styles.instructionsValue}>{activeSession.verification_uri_complete}</Text>
              <Text style={styles.instructionsLabel}>verification_uri</Text>
              <Text style={styles.instructionsValue}>{activeSession.verification_uri}</Text>
              <Text style={styles.instructionsLabel}>user_code</Text>
              <Text style={styles.codeValue}>{activeSession.user_code}</Text>
            </View>
          </>
        ) : null}
        <View style={styles.footerRow}>
          <View style={styles.statusPanel}>
            <Text style={styles.statusHeading}>Polling State</Text>
            <Text style={styles.statusCopy}>{statusCopyForState(pollState)}</Text>
            <Text style={styles.statusMeta}>Expires in {secondsRemaining}s</Text>
            <Text style={styles.statusMeta}>
              Poll interval {activeSession?.interval ?? DEFAULT_POLL_INTERVAL_SECONDS}s
            </Text>
            {restoreMessage ? (
              <Text style={styles.statusMeta}>{restoreMessage}</Text>
            ) : null}
          </View>
          {linkedSession ? (
            <Pressable
              hasTVPreferredFocus
              onPress={() => void handleLogout()}
              style={({ focused, pressed }) => [
                styles.refreshButton,
                focused ? styles.refreshButtonFocused : undefined,
                pressed ? styles.refreshButtonPressed : undefined,
              ]}
            >
              <Text style={styles.refreshButtonText}>Sign out TV</Text>
            </Pressable>
          ) : (
            <Pressable
              hasTVPreferredFocus
              onPress={() => void handleRefreshCode()}
              style={({ focused, pressed }) => [
                styles.refreshButton,
                focused ? styles.refreshButtonFocused : undefined,
                pressed ? styles.refreshButtonPressed : undefined,
              ]}
            >
              <Text style={styles.refreshButtonText}>Refresh code</Text>
            </Pressable>
          )}
        </View>
      </View>
      {linkedSession ? <SignedInPanel token={linkedSession.accessToken} /> : null}
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
