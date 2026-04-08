import type { CSSProperties, ReactNode } from "react"

import { nurtDesignTokens } from "@generated/design-tokens"

import { Eyebrow } from "./eyebrow"

export interface ActionClusterProps {
  heading: string
  note: string
  children?: ReactNode
}

const panelStyle: CSSProperties = {
  display: "grid",
  gap: nurtDesignTokens.spacing.md,
  padding: nurtDesignTokens.spacing.lg,
  borderRadius: nurtDesignTokens.radius.lg,
  border: `1px solid ${nurtDesignTokens.colors.border}`,
  backgroundColor: nurtDesignTokens.colors.surfaceChrome,
}

const headingStyle: CSSProperties = {
  margin: 0,
  fontFamily: nurtDesignTokens.typography.display,
  fontSize: "1.05rem",
}

const actionsStyle: CSSProperties = {
  display: "flex",
  gap: nurtDesignTokens.spacing.sm,
  flexWrap: "wrap",
}

const noteStyle: CSSProperties = {
  margin: 0,
  color: nurtDesignTokens.colors.mutedForeground,
}

export function ActionCluster({ heading, note, children }: ActionClusterProps) {
  return (
    <section style={panelStyle}>
      <div style={{ display: "grid", gap: nurtDesignTokens.spacing.xs }}>
        <Eyebrow tone="muted">Action Cluster</Eyebrow>
        <h2 style={headingStyle}>{heading}</h2>
      </div>
      <div className="nurt-actions" style={actionsStyle}>
        {children}
      </div>
      <p className="nurt-copy" style={noteStyle}>
        {note}
      </p>
    </section>
  )
}
