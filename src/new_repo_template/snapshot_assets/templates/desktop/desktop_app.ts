import { nurtDesignTokens } from "@generated/design-tokens"
import {
  NURT_FRONTEND_COPY,
  NURT_GETTING_STARTED_STEPS,
  NURT_WELCOME_HIGHLIGHTS,
} from "@generated/shared"
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
  width: "min(42rem, 100%)",
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

const copyStyle = {
  margin: 0,
  color: nurtDesignTokens.colors.mutedForeground,
  lineHeight: 1.6,
}

const sectionStyle = {
  display: "grid",
  gap: nurtDesignTokens.spacing.sm,
}

const sectionHeadingStyle = {
  margin: 0,
  fontFamily: nurtDesignTokens.typography.display,
  fontSize: "1.05rem",
}

const cardListStyle = {
  display: "grid",
  gap: nurtDesignTokens.spacing.sm,
}

const cardStyle = {
  display: "grid",
  gap: nurtDesignTokens.spacing.xs,
  padding: nurtDesignTokens.spacing.md,
  borderRadius: nurtDesignTokens.radius.md,
  border: `1px solid ${nurtDesignTokens.colors.border}`,
  backgroundColor: nurtDesignTokens.colors.surfaceRaised,
}

const cardTitleStyle = {
  margin: 0,
  fontWeight: 600,
}

const stepRowStyle = {
  display: "grid",
  gridTemplateColumns: "1.75rem 1fr",
  gap: nurtDesignTokens.spacing.sm,
  alignItems: "start",
}

const stepIndexStyle = {
  width: "1.75rem",
  height: "1.75rem",
  display: "grid",
  placeItems: "center",
  borderRadius: nurtDesignTokens.radius.pill,
  backgroundColor: nurtDesignTokens.colors.accent,
  color: nurtDesignTokens.colors.background,
  fontWeight: 700,
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

export function DesktopWelcomePage() {
  return createElement(
    "main",
    { style: shellStyle },
    createElement(
      "section",
      { style: panelStyle },
      createElement("p", { style: eyebrowStyle }, NURT_FRONTEND_COPY.eyebrow),
      createElement("h1", null, NURT_FRONTEND_COPY.title),
      createElement("p", { style: copyStyle }, NURT_FRONTEND_COPY.body),
      createElement(
        "section",
        { style: sectionStyle },
        createElement(
          "h2",
          { style: sectionHeadingStyle },
          NURT_FRONTEND_COPY.highlightsHeading,
        ),
        createElement(
          "div",
          { style: cardListStyle },
          ...NURT_WELCOME_HIGHLIGHTS.map((highlight) =>
            createElement(
              "div",
              { key: highlight.title, style: cardStyle },
              createElement("p", { style: cardTitleStyle }, highlight.title),
              createElement("p", { style: copyStyle }, highlight.body),
            ),
          ),
        ),
      ),
      createElement(
        "section",
        { style: sectionStyle },
        createElement(
          "h2",
          { style: sectionHeadingStyle },
          NURT_FRONTEND_COPY.gettingStartedHeading,
        ),
        createElement(
          "div",
          { style: cardListStyle },
          ...NURT_GETTING_STARTED_STEPS.map((step, index) =>
            createElement(
              "div",
              { key: step, style: stepRowStyle },
              createElement("div", { style: stepIndexStyle }, index + 1),
              createElement("p", { style: copyStyle }, step),
            ),
          ),
        ),
      ),
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
      createElement("p", { style: copyStyle }, NURT_FRONTEND_COPY.caption),
    ),
  )
}
