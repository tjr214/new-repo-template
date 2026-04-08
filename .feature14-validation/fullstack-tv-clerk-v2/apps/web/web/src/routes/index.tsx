import { createFileRoute } from "@tanstack/react-router"

import { nurtDesignTokens } from "@generated/design-tokens"
import {
  NURT_GETTING_STARTED_STEPS,
  NURT_WELCOME_ACTIONS,
  NURT_WELCOME_HERO,
  NURT_WELCOME_SECTIONS,
  NURT_WELCOME_HIGHLIGHTS,
} from "@generated/shared"
import { ActionCluster } from "@generated/ui/components/action-cluster"
import { Button } from "@generated/ui/components/button"
import { FeatureCard } from "@generated/ui/components/feature-card"
import { HeroPanel } from "@generated/ui/components/hero-panel"
import { SectionFrame } from "@generated/ui/components/section-frame"
import { StepList } from "@generated/ui/components/step-list"

const pageStyle = {
  backgroundColor: nurtDesignTokens.colors.background,
  color: nurtDesignTokens.colors.foreground,
}

const panelStyle = {
  width: "min(78rem, 100%)",
  display: "grid",
  gap: nurtDesignTokens.spacing.lg,
}

const consoleGridStyle = {
  display: "grid",
  gap: nurtDesignTokens.spacing.md,
}

const sectionColumnStyle = {
  display: "grid",
  gap: nurtDesignTokens.spacing.md,
}

const cardListStyle = {
  display: "grid",
  gap: nurtDesignTokens.spacing.sm,
}

const footerGridStyle = {
  display: "grid",
  gap: nurtDesignTokens.spacing.md,
}

const captionStyle = {
  margin: 0,
  color: nurtDesignTokens.colors.mutedForeground,
}

export const Route = createFileRoute("/")({
  component: HomePage,
})

function HomePage() {
  return (
    <main className="nurt-shell" style={pageStyle}>
      <section className="nurt-panel" style={panelStyle}>
        <div className="nurt-panel-grid" style={consoleGridStyle}>
          <HeroPanel
            eyebrow={NURT_WELCOME_HERO.eyebrow}
            label={NURT_WELCOME_HERO.label}
            title={NURT_WELCOME_HERO.title}
            body={NURT_WELCOME_HERO.body}
            status={NURT_WELCOME_HERO.status}
          />
          <div style={sectionColumnStyle}>
            <SectionFrame heading={NURT_WELCOME_SECTIONS.highlightsHeading} label="Shared Layer">
              <div style={cardListStyle}>
                {NURT_WELCOME_HIGHLIGHTS.map((highlight) => (
                  <FeatureCard
                    key={highlight.title}
                    meta={highlight.meta}
                    title={highlight.title}
                    body={highlight.body}
                  />
                ))}
              </div>
            </SectionFrame>
            <SectionFrame heading={NURT_WELCOME_SECTIONS.gettingStartedHeading} label="Execution Lane">
              <StepList steps={NURT_GETTING_STARTED_STEPS} />
            </SectionFrame>
          </div>
        </div>
        <div style={footerGridStyle}>
          <ActionCluster
            heading={NURT_WELCOME_SECTIONS.actionsHeading}
            note={NURT_WELCOME_HERO.caption}
          >
            <Button>{NURT_WELCOME_ACTIONS.primary}</Button>
            <Button tone="secondary">{NURT_WELCOME_ACTIONS.secondary}</Button>
          </ActionCluster>
          <p className="nurt-copy" style={captionStyle}>
            {NURT_WELCOME_HERO.caption}
          </p>
        </div>
      </section>
    </main>
  )
}
