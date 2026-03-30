import { nurtDesignTokens } from "@generated/design-tokens"
import { NURT_FRONTEND_COPY } from "@generated/shared"
import { createElement } from "react"

const shellStyle = {
  minHeight: "100vh",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  padding: nurtDesignTokens.spacing.xl,
  backgroundColor: nurtDesignTokens.colors.background,
  color: nurtDesignTokens.colors.foreground,
  fontFamily: nurtDesignTokens.typography.body,
}

const panelStyle = {
  width: "min(36rem, 100%)",
  display: "grid",
  gap: nurtDesignTokens.spacing.md,
  padding: nurtDesignTokens.spacing.xl,
  borderRadius: nurtDesignTokens.radius.lg,
  border: `1px solid ${nurtDesignTokens.colors.border}`,
  backgroundColor: nurtDesignTokens.colors.surface,
  boxShadow: nurtDesignTokens.shadow.strong,
}

const eyebrowStyle = {
  margin: 0,
  letterSpacing: "0.16em",
  textTransform: "uppercase" as const,
  fontSize: "0.8rem",
  fontWeight: 700,
  color: nurtDesignTokens.colors.accent,
}

const captionStyle = {
  margin: 0,
  color: nurtDesignTokens.colors.mutedForeground,
  lineHeight: 1.6,
}

const buttonRowStyle = {
  display: "flex",
  gap: nurtDesignTokens.spacing.sm,
  flexWrap: "wrap" as const,
}

const primaryButtonStyle = {
  border: `1px solid ${nurtDesignTokens.colors.accent}`,
  borderRadius: nurtDesignTokens.radius.pill,
  backgroundColor: nurtDesignTokens.colors.accent,
  color: nurtDesignTokens.colors.background,
  padding: `${nurtDesignTokens.spacing.sm} ${nurtDesignTokens.spacing.lg}`,
  fontWeight: 600,
}

const secondaryButtonStyle = {
  ...primaryButtonStyle,
  border: `1px solid ${nurtDesignTokens.colors.border}`,
  backgroundColor: nurtDesignTokens.colors.surfaceRaised,
  color: nurtDesignTokens.colors.foreground,
}

export function DesktopHelloWorldPage() {
  return createElement(
    "main",
    { style: shellStyle },
    createElement(
      "section",
      { style: panelStyle },
      createElement("p", { style: eyebrowStyle }, NURT_FRONTEND_COPY.eyebrow),
      createElement("h1", null, NURT_FRONTEND_COPY.title),
      createElement("p", { style: captionStyle }, NURT_FRONTEND_COPY.body),
      createElement(
        "div",
        { style: buttonRowStyle },
        createElement(
          "button",
          { type: "button", style: primaryButtonStyle },
          NURT_FRONTEND_COPY.primaryAction,
        ),
        createElement(
          "button",
          { type: "button", style: secondaryButtonStyle },
          NURT_FRONTEND_COPY.secondaryAction,
        ),
      ),
      createElement("p", { style: captionStyle }, NURT_FRONTEND_COPY.caption),
    ),
  )
}
