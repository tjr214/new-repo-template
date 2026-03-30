import { createFileRoute } from "@tanstack/react-router"

import { nurtDesignTokens } from "@generated/design-tokens"
import { NURT_FRONTEND_COPY } from "@generated/shared"
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
