import { useMemo, useState } from "react"

import { Link, createFileRoute } from "@tanstack/react-router"

import { nurtDesignTokens } from "@generated/design-tokens"

import { authClient } from "../auth-client"
import { activeAuthConfig } from "../auth-runtime"

interface DeviceRouteSearch {
  user_code?: string
}

interface DeviceApproveError {
  error: string
  error_description: string
}

const pageStyle = {
  minHeight: "100vh",
  display: "grid",
  placeItems: "center",
  backgroundColor: nurtDesignTokens.colors.background,
  color: nurtDesignTokens.colors.foreground,
  padding: nurtDesignTokens.spacing.lg,
}

const cardStyle = {
  width: "min(42rem, 100%)",
  display: "grid",
  gap: nurtDesignTokens.spacing.md,
  borderRadius: nurtDesignTokens.radius.lg,
  border: `1px solid ${nurtDesignTokens.colors.border}`,
  backgroundColor: nurtDesignTokens.colors.surface,
  padding: nurtDesignTokens.spacing.lg,
}

const codeStyle = {
  margin: 0,
  fontSize: "2rem",
  fontWeight: 700,
  letterSpacing: "0.14em",
}

const fieldStyle = {
  borderRadius: nurtDesignTokens.radius.md,
  border: `1px solid ${nurtDesignTokens.colors.border}`,
  backgroundColor: nurtDesignTokens.colors.background,
  color: nurtDesignTokens.colors.foreground,
  padding: nurtDesignTokens.spacing.sm,
}

const buttonRowStyle = {
  display: "flex",
  gap: nurtDesignTokens.spacing.sm,
  flexWrap: "wrap" as const,
  alignItems: "center",
}

const buttonStyle = {
  borderRadius: nurtDesignTokens.radius.md,
  border: `1px solid ${nurtDesignTokens.colors.border}`,
  backgroundColor: nurtDesignTokens.colors.accent,
  color: nurtDesignTokens.colors.background,
  cursor: "pointer",
  padding: `${nurtDesignTokens.spacing.sm} ${nurtDesignTokens.spacing.md}`,
}

const secondaryButtonStyle = {
  ...buttonStyle,
  backgroundColor: nurtDesignTokens.colors.surface,
  color: nurtDesignTokens.colors.foreground,
}

const authBlockStyle = {
  display: "grid",
  gap: nurtDesignTokens.spacing.sm,
  borderRadius: nurtDesignTokens.radius.md,
  border: `1px solid ${nurtDesignTokens.colors.border}`,
  padding: nurtDesignTokens.spacing.md,
}

const apiBaseUrl = import.meta.env.VITE_DEVICE_LINK_API_URL ?? import.meta.env.VITE_CONVEX_URL

export const Route = createFileRoute("/device")({
  validateSearch: (search: Record<string, unknown>): DeviceRouteSearch => ({
    user_code: typeof search.user_code === "string" ? search.user_code : undefined,
  }),
  component: DeviceRoutePage,
})

async function approveDeviceLink({
  userCode,
  accessToken,
}: {
  userCode: string
  accessToken: string
}) {
  const response = await fetch(`${apiBaseUrl}/device/approve`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${accessToken}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ user_code: userCode }),
  })
  if (response.ok) {
    return { success: true as const }
  }
  const error = (await response.json()) as DeviceApproveError
  throw new Error(error.error_description || error.error)
}

function DeviceRoutePage() {
  const search = Route.useSearch()
  const { data: session, isPending } = authClient.useSession()
  const [userCode, setUserCode] = useState(search.user_code ?? "")
  const [email, setEmail] = useState("operator@nurt.local")
  const [password, setPassword] = useState("nurt-demo-password")
  const [approvalState, setApprovalState] = useState<"idle" | "submitting" | "approved" | "error">("idle")
  const [statusMessage, setStatusMessage] = useState(
    "Use the local Better Auth session to approve the pending TV device code.",
  )

  const currentUserLabel = useMemo(() => {
    return session?.user?.email ?? session?.user?.name ?? "Signed-out user"
  }, [session])

  async function handleCreateAccount() {
    setStatusMessage("Creating local Better Auth user...")
    try {
      await authClient.signUp.email({
        email,
        password,
        name: email,
      })
      setStatusMessage("Account created. You can now approve the TV request.")
    } catch (error) {
      setStatusMessage(error instanceof Error ? error.message : "Sign-up failed.")
    }
  }

  async function handleSignIn() {
    setStatusMessage("Signing into Better Auth...")
    try {
      await authClient.signIn.email({ email, password })
      setStatusMessage("Signed in. You can now approve the TV request.")
    } catch (error) {
      setStatusMessage(error instanceof Error ? error.message : "Sign-in failed.")
    }
  }

  async function handleSignOut() {
    await authClient.signOut()
    setStatusMessage("Signed out of the local Better Auth session.")
  }

  async function handleApprove() {
    if (!userCode.trim()) {
      setApprovalState("error")
      setStatusMessage("Enter the TV user code before approving this request.")
      return
    }
    const tokenResponse = await authClient.convex.token({
      fetchOptions: { throw: false },
    })
    const accessToken = tokenResponse.data?.token ?? null
    if (!accessToken) {
      setApprovalState("error")
      setStatusMessage("Better Auth did not return a Convex token for this approval request.")
      return
    }
    setApprovalState("submitting")
    setStatusMessage("Submitting approval to the backend...")
    try {
      await approveDeviceLink({ userCode: userCode.trim().toUpperCase(), accessToken })
      setApprovalState("approved")
      setStatusMessage("TV approved. The TV app can now redeem the device code into its app session.")
    } catch (error) {
      setApprovalState("error")
      setStatusMessage(error instanceof Error ? error.message : "Approval failed.")
    }
  }

  return (
    <main style={pageStyle}>
      <section style={cardStyle}>
        <p style={{ margin: 0, color: nurtDesignTokens.colors.mutedForeground }}>
          TV Device-Link Verification
        </p>
        <h1 style={{ margin: 0 }}>Approve This TV</h1>
        <p style={{ margin: 0 }}>
          This route signs in through the local Better Auth session, then sends a real approval
          request to the backend-owned device-link flow.
        </p>
        <p style={{ margin: 0 }}>
          Active provider boundary: <strong>{activeAuthConfig.provider}</strong>
        </p>
        <div style={authBlockStyle}>
          <p style={{ margin: 0, color: nurtDesignTokens.colors.mutedForeground }}>Current web user</p>
          <p style={{ margin: 0 }}>{currentUserLabel}</p>
          <label style={{ display: "grid", gap: nurtDesignTokens.spacing.xs }}>
            <span>Email</span>
            <input onChange={(event) => setEmail(event.target.value)} style={fieldStyle} value={email} />
          </label>
          <label style={{ display: "grid", gap: nurtDesignTokens.spacing.xs }}>
            <span>Password</span>
            <input
              onChange={(event) => setPassword(event.target.value)}
              style={fieldStyle}
              type="password"
              value={password}
            />
          </label>
          <div style={buttonRowStyle}>
            <button onClick={() => void handleCreateAccount()} style={secondaryButtonStyle} type="button">
              Create Account
            </button>
            <button onClick={() => void handleSignIn()} style={buttonStyle} type="button">
              Sign In
            </button>
            {session ? (
              <button onClick={() => void handleSignOut()} style={secondaryButtonStyle} type="button">
                Sign Out
              </button>
            ) : null}
          </div>
          {isPending ? (
            <p style={{ margin: 0, color: nurtDesignTokens.colors.mutedForeground }}>
              Loading Better Auth session...
            </p>
          ) : null}
        </div>
        <div>
          <p style={{ margin: 0, color: nurtDesignTokens.colors.mutedForeground }}>Enter or confirm the user code</p>
          <p style={codeStyle}>{userCode.trim().toUpperCase() || "ENTER-CODE"}</p>
        </div>
        <label style={{ display: "grid", gap: nurtDesignTokens.spacing.xs }}>
          <span>Manual code entry</span>
          <input
            aria-label="Device link user code"
            onChange={(event) => setUserCode(event.target.value.toUpperCase())}
            style={fieldStyle}
            value={userCode}
          />
        </label>
        <div style={buttonRowStyle}>
          <button onClick={() => void handleApprove()} style={buttonStyle} type="button">
            {approvalState === "submitting" ? "Approving..." : "Approve This TV"}
          </button>
          <Link style={secondaryButtonStyle} to="/">
            Back To Operator Console
          </Link>
        </div>
        <p style={{ margin: 0, color: nurtDesignTokens.colors.mutedForeground }}>
          {statusMessage}
        </p>
      </section>
    </main>
  )
}
