import { createFileRoute } from "@tanstack/react-router"

import { nurtDesignTokens } from "@generated/design-tokens"
import {
  NURT_FRONTEND_COPY,
  NURT_GETTING_STARTED_STEPS,
  NURT_WELCOME_HIGHLIGHTS,
} from "@generated/shared"
import { Button } from "@generated/ui/components/button"

const pageStyle = {
  backgroundColor: nurtDesignTokens.colors.background,
  color: nurtDesignTokens.colors.foreground,
}

const panelStyle = {
  backgroundColor: nurtDesignTokens.colors.surface,
  border: `1px solid ${nurtDesignTokens.colors.border}`,
  borderRadius: nurtDesignTokens.radius.lg,
  boxShadow: nurtDesignTokens.shadow.strong,
}

const captionStyle = {
  color: nurtDesignTokens.colors.mutedForeground,
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

const listStyle = {
  display: "grid",
  gap: nurtDesignTokens.spacing.sm,
  margin: 0,
  padding: 0,
  listStyle: "none",
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
  padding: `${nurtDesignTokens.spacing.sm} 0`,
  borderBottom: `1px solid ${nurtDesignTokens.colors.border}`,
}

const stepIndexStyle = {
  display: "grid",
  placeItems: "center",
  width: "1.75rem",
  height: "1.75rem",
  borderRadius: nurtDesignTokens.radius.pill,
  backgroundColor: nurtDesignTokens.colors.accent,
  color: nurtDesignTokens.colors.background,
  fontWeight: 700,
}

export const Route = createFileRoute("/")({
  component: HomePage,
})

function HomePage() {
  return (
    <main className="nurt-shell" style={pageStyle}>
      <section className="nurt-panel" style={panelStyle}>
        <p className="nurt-eyebrow">{NURT_FRONTEND_COPY.eyebrow}</p>
        <h1>{NURT_FRONTEND_COPY.title}</h1>
        <p className="nurt-copy">{NURT_FRONTEND_COPY.body}</p>
        <section style={sectionStyle}>
          <h2 style={sectionHeadingStyle}>{NURT_FRONTEND_COPY.highlightsHeading}</h2>
          <ul style={listStyle}>
            {NURT_WELCOME_HIGHLIGHTS.map((highlight) => (
              <li key={highlight.title} style={cardStyle}>
                <p style={cardTitleStyle}>{highlight.title}</p>
                <p className="nurt-copy">{highlight.body}</p>
              </li>
            ))}
          </ul>
        </section>
        <section style={sectionStyle}>
          <h2 style={sectionHeadingStyle}>{NURT_FRONTEND_COPY.gettingStartedHeading}</h2>
          <ol style={listStyle}>
            {NURT_GETTING_STARTED_STEPS.map((step, index) => (
              <li key={step} style={stepRowStyle}>
                <span style={stepIndexStyle}>{index + 1}</span>
                <span className="nurt-copy">{step}</span>
              </li>
            ))}
          </ol>
        </section>
        <div className="nurt-actions">
          <Button>{NURT_FRONTEND_COPY.primaryAction}</Button>
          <Button tone="secondary">{NURT_FRONTEND_COPY.secondaryAction}</Button>
        </div>
        <p className="nurt-copy" style={captionStyle}>
          {NURT_FRONTEND_COPY.caption}
        </p>
      </section>
    </main>
  )
}
