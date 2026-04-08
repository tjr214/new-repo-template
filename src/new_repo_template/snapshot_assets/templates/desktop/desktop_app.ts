import { nurtDesignTokens } from "@generated/design-tokens"
import {
  NURT_GETTING_STARTED_STEPS,
  NURT_WELCOME_ACTIONS,
  NURT_WELCOME_HERO,
  NURT_WELCOME_SECTIONS,
  NURT_WELCOME_HIGHLIGHTS,
} from "@generated/shared"
import { createElement } from "react"

const shellStyle = {
  minHeight: "100vh",
  display: "flex",
  justifyContent: "center",
  padding: nurtDesignTokens.spacing.xl,
  backgroundColor: nurtDesignTokens.colors.background,
  color: nurtDesignTokens.colors.foreground,
  fontFamily: nurtDesignTokens.typography.body,
}

const panelStyle = {
  width: "min(78rem, 100%)",
  display: "grid",
  gap: nurtDesignTokens.spacing.lg,
}

const consoleGridStyle = {
  display: "grid",
  gap: nurtDesignTokens.spacing.md,
  gridTemplateColumns: "minmax(0, 1.4fr) minmax(21rem, 0.9fr)",
  alignItems: "start",
}

const copyStyle = {
  margin: 0,
  color: nurtDesignTokens.colors.mutedForeground,
  lineHeight: 1.6,
}

const sectionColumnStyle = {
  display: "grid",
  gap: nurtDesignTokens.spacing.md,
}

const heroPanelStyle = {
  display: "grid",
  gap: nurtDesignTokens.spacing.lg,
  padding: nurtDesignTokens.spacing.xl,
  borderRadius: nurtDesignTokens.radius.lg,
  border: `1px solid ${nurtDesignTokens.colors.border}`,
  background: `linear-gradient(160deg, ${nurtDesignTokens.colors.surface} 0%, ${nurtDesignTokens.colors.surfaceChrome} 100%)`,
  boxShadow: nurtDesignTokens.shadow.strong,
}

const headerRowStyle = {
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  gap: nurtDesignTokens.spacing.md,
  flexWrap: "wrap" as const,
}

const eyebrowStyle = {
  margin: 0,
  letterSpacing: "0.16em",
  textTransform: "uppercase" as const,
  fontSize: "0.8rem",
  fontWeight: 700,
  color: nurtDesignTokens.colors.accent,
}

const labelStyle = {
  display: "inline-flex",
  alignItems: "center",
  padding: `${nurtDesignTokens.spacing.xs} ${nurtDesignTokens.spacing.sm}`,
  borderRadius: nurtDesignTokens.radius.pill,
  backgroundColor: nurtDesignTokens.colors.surfaceRaised,
  border: `1px solid ${nurtDesignTokens.colors.border}`,
  color: nurtDesignTokens.colors.accentMuted,
  fontSize: "0.85rem",
  fontWeight: 700,
}

const heroTitleStyle = {
  margin: 0,
  fontFamily: nurtDesignTokens.typography.display,
  fontSize: "3.6rem",
  lineHeight: 1,
}

const statusStyle = {
  display: "inline-flex",
  alignItems: "center",
  gap: nurtDesignTokens.spacing.xs,
  width: "fit-content",
  padding: `${nurtDesignTokens.spacing.xs} ${nurtDesignTokens.spacing.sm}`,
  borderRadius: nurtDesignTokens.radius.pill,
  backgroundColor: nurtDesignTokens.colors.surfaceRaised,
  border: `1px solid ${nurtDesignTokens.colors.border}`,
}

const statusDotStyle = {
  width: "0.55rem",
  height: "0.55rem",
  borderRadius: nurtDesignTokens.radius.pill,
  backgroundColor: nurtDesignTokens.colors.accent,
}

const sectionStyle = {
  display: "grid",
  gap: nurtDesignTokens.spacing.md,
  padding: nurtDesignTokens.spacing.lg,
  borderRadius: nurtDesignTokens.radius.lg,
  border: `1px solid ${nurtDesignTokens.colors.border}`,
  backgroundColor: nurtDesignTokens.colors.surface,
  boxShadow: nurtDesignTokens.shadow.glow,
}

const sectionLabelStyle = {
  ...eyebrowStyle,
  color: nurtDesignTokens.colors.mutedForeground,
}

const sectionHeadingStyle = {
  margin: 0,
  fontFamily: nurtDesignTokens.typography.display,
  fontSize: "1.15rem",
}

const cardListStyle = {
  display: "grid",
  gap: nurtDesignTokens.spacing.sm,
}

const cardStyle = {
  display: "grid",
  gap: nurtDesignTokens.spacing.sm,
  padding: nurtDesignTokens.spacing.md,
  borderRadius: nurtDesignTokens.radius.md,
  border: `1px solid ${nurtDesignTokens.colors.border}`,
  backgroundColor: nurtDesignTokens.colors.surfaceRaised,
}

const cardMetaStyle = {
  ...sectionLabelStyle,
  margin: 0,
}

const cardTitleStyle = {
  margin: 0,
  fontWeight: 650,
}

const stepRowStyle = {
  display: "grid",
  gridTemplateColumns: "2rem 1fr",
  gap: nurtDesignTokens.spacing.sm,
  alignItems: "start",
  padding: `${nurtDesignTokens.spacing.sm} 0`,
  borderBottom: `1px solid ${nurtDesignTokens.colors.border}`,
}

const stepIndexStyle = {
  width: "2rem",
  height: "2rem",
  display: "grid",
  placeItems: "center",
  borderRadius: nurtDesignTokens.radius.pill,
  backgroundColor: nurtDesignTokens.colors.accent,
  color: nurtDesignTokens.colors.background,
  fontWeight: 700,
}

const stepTitleStyle = {
  margin: 0,
  fontWeight: 650,
}

const buttonRowStyle = {
  display: "flex",
  gap: nurtDesignTokens.spacing.sm,
  flexWrap: "wrap" as const,
}

const actionClusterStyle = {
  display: "grid",
  gap: nurtDesignTokens.spacing.md,
  padding: nurtDesignTokens.spacing.lg,
  borderRadius: nurtDesignTokens.radius.lg,
  border: `1px solid ${nurtDesignTokens.colors.border}`,
  backgroundColor: nurtDesignTokens.colors.surfaceChrome,
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

function DesktopHeroPanel() {
  return createElement(
    "section",
    { style: heroPanelStyle },
    createElement(
      "div",
      { style: headerRowStyle },
      createElement("p", { style: eyebrowStyle }, NURT_WELCOME_HERO.eyebrow),
      createElement("span", { style: labelStyle }, NURT_WELCOME_HERO.label),
    ),
    createElement(
      "div",
      { style: sectionColumnStyle },
      createElement("h1", { style: heroTitleStyle }, NURT_WELCOME_HERO.title),
      createElement("p", { style: copyStyle }, NURT_WELCOME_HERO.body),
    ),
    createElement(
      "div",
      { style: statusStyle },
      createElement("span", { style: statusDotStyle }),
      createElement("span", null, NURT_WELCOME_HERO.status),
    ),
  )
}

function DesktopFeatureCard(props: (typeof NURT_WELCOME_HIGHLIGHTS)[number]) {
  return createElement(
    "div",
    { key: props.title, style: cardStyle },
    createElement("p", { style: cardMetaStyle }, props.meta),
    createElement("p", { style: cardTitleStyle }, props.title),
    createElement("p", { style: copyStyle }, props.body),
  )
}

function DesktopStepList() {
  return createElement(
    "div",
    { style: cardListStyle },
    ...NURT_GETTING_STARTED_STEPS.map((step, index) =>
      createElement(
        "div",
        { key: step.title, style: stepRowStyle },
        createElement("div", { style: stepIndexStyle }, index + 1),
        createElement(
          "div",
          { style: sectionColumnStyle },
          createElement("p", { style: stepTitleStyle }, step.title),
          createElement("p", { style: copyStyle }, step.body),
        ),
      ),
    ),
  )
}

function DesktopActionCluster() {
  return createElement(
    "section",
    { style: actionClusterStyle },
    createElement("p", { style: sectionLabelStyle }, "Action Cluster"),
    createElement(
      "h2",
      { style: sectionHeadingStyle },
      NURT_WELCOME_SECTIONS.actionsHeading,
    ),
    createElement(
      "div",
      { style: buttonRowStyle },
      createElement(
        "button",
        { type: "button", style: primaryButtonStyle },
        NURT_WELCOME_ACTIONS.primary,
      ),
      createElement(
        "button",
        { type: "button", style: secondaryButtonStyle },
        NURT_WELCOME_ACTIONS.secondary,
      ),
    ),
    createElement("p", { style: copyStyle }, NURT_WELCOME_HERO.caption),
  )
}

export function DesktopWelcomePage() {
  return createElement(
    "main",
    { style: shellStyle },
    createElement(
      "section",
      { style: panelStyle },
      createElement(
        "div",
        { style: consoleGridStyle },
        createElement(DesktopHeroPanel),
        createElement(
          "div",
          { style: sectionColumnStyle },
          createElement(
            "section",
            { style: sectionStyle },
            createElement("p", { style: sectionLabelStyle }, "Shared Layer"),
            createElement(
              "h2",
              { style: sectionHeadingStyle },
              NURT_WELCOME_SECTIONS.highlightsHeading,
            ),
            createElement(
              "div",
              { style: cardListStyle },
              ...NURT_WELCOME_HIGHLIGHTS.map((highlight) =>
                createElement(DesktopFeatureCard, { key: highlight.title, ...highlight }),
              ),
            ),
          ),
          createElement(
            "section",
            { style: sectionStyle },
            createElement("p", { style: sectionLabelStyle }, "Execution Lane"),
            createElement(
              "h2",
              { style: sectionHeadingStyle },
              NURT_WELCOME_SECTIONS.gettingStartedHeading,
            ),
            createElement(DesktopStepList),
          ),
        ),
      ),
      createElement(DesktopActionCluster),
    ),
  )
}
