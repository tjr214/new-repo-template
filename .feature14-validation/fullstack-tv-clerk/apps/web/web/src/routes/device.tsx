import { useState } from "react"

import { Link, createFileRoute } from "@tanstack/react-router"

import { nurtDesignTokens } from "@generated/design-tokens"

import { activeAuthConfig } from "../auth-runtime"

interface DeviceRouteSearch {
  user_code?: string
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
  width: "min(38rem, 100%)",
  display: "grid",
  gap: nurtDesignTokens.spacing.md,
  borderRadius: nurtDesignTokens.radii.lg,
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
  borderRadius: nurtDesignTokens.radii.md,
  border: `1px solid ${nurtDesignTokens.colors.border}`,
  backgroundColor: nurtDesignTokens.colors.background,
  color: nurtDesignTokens.colors.foreground,
  padding: nurtDesignTokens.spacing.sm,
}

const buttonRowStyle = {
  display: "flex",
  gap: nurtDesignTokens.spacing.sm,
  flexWrap: "wrap" as const,
}

const buttonStyle = {
  borderRadius: nurtDesignTokens.radii.md,
  border: `1px solid ${nurtDesignTokens.colors.border}`,
  backgroundColor: nurtDesignTokens.colors.accent,
  color: nurtDesignTokens.colors.accentForeground,
  cursor: "pointer",
  padding: `${nurtDesignTokens.spacing.sm} ${nurtDesignTokens.spacing.md}`,
}

const secondaryButtonStyle = {
  ...buttonStyle,
  backgroundColor: nurtDesignTokens.colors.surface,
  color: nurtDesignTokens.colors.foreground,
}

export const Route = createFileRoute("/device")({
  validateSearch: (search: Record<string, unknown>): DeviceRouteSearch => ({
    user_code: typeof search.user_code === "string" ? search.user_code : undefined,
  }),
  component: DeviceRoutePage,
})

function DeviceRoutePage() {
  const search = Route.useSearch()
  const [userCode, setUserCode] = useState(search.user_code ?? "NURT-1400")
  const [approvalState, setApprovalState] = useState<"review" | "approved">("review")

  return (
    <main style={pageStyle}>
      <section style={cardStyle}>
        <p style={{ margin: 0, color: nurtDesignTokens.colors.mutedForeground }}>
          TV Device-Link Verification
        </p>
        <h1 style={{ margin: 0 }}>Approve This TV</h1>
        <p style={{ margin: 0 }}>
          This route stays provider-neutral. Complete sign-in through the active web auth
          boundary, then approve the pending TV code against the backend-owned device-link
          record.
        </p>
        <p style={{ margin: 0 }}>
          Active provider boundary: <strong>{activeAuthConfig.provider}</strong>
        </p>
        <div>
          <p style={{ margin: 0, color: nurtDesignTokens.colors.mutedForeground }}>
            Enter or confirm the user code
          </p>
          <p style={codeStyle}>{userCode}</p>
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
          <button onClick={() => setApprovalState("approved")} style={buttonStyle} type="button">
            Approve This TV
          </button>
          <Link style={secondaryButtonStyle} to="/">
            Back To Operator Console
          </Link>
        </div>
        <p style={{ margin: 0, color: nurtDesignTokens.colors.mutedForeground }}>
          {approvalState === "approved"
            ? "Starter approval state reached. Replace this local UI state with real backend approval and session redemption."
            : "Starter review state active. Replace this local UI state with the real signed-in approval flow for your chosen auth provider."}
        </p>
        <p style={{ margin: 0, color: nurtDesignTokens.colors.mutedForeground }}>
          The matching TV app should poll `/device/token` while the backend owns the short-lived
          record, expiry, and final app-session redemption.
        </p>
      </section>
    </main>
  )
}
