import type { CSSProperties } from "react"

import { nurtDesignTokens } from "@generated/design-tokens"

export interface StepListItem {
  title: string
  body: string
}

export interface StepListProps {
  steps: ReadonlyArray<StepListItem>
}

const listStyle: CSSProperties = {
  display: "grid",
  gap: nurtDesignTokens.spacing.sm,
  margin: 0,
  padding: 0,
  listStyle: "none",
}

const rowStyle: CSSProperties = {
  display: "grid",
  gridTemplateColumns: "2rem 1fr",
  gap: nurtDesignTokens.spacing.sm,
  alignItems: "start",
  padding: `${nurtDesignTokens.spacing.sm} 0`,
  borderBottom: `1px solid ${nurtDesignTokens.colors.border}`,
}

const indexStyle: CSSProperties = {
  display: "grid",
  placeItems: "center",
  width: "2rem",
  height: "2rem",
  borderRadius: nurtDesignTokens.radius.pill,
  backgroundColor: nurtDesignTokens.colors.accent,
  color: nurtDesignTokens.colors.background,
  fontWeight: 700,
}

const titleStyle: CSSProperties = {
  margin: 0,
  fontWeight: 650,
}

const bodyStyle: CSSProperties = {
  margin: 0,
  color: nurtDesignTokens.colors.mutedForeground,
}

export function StepList({ steps }: StepListProps) {
  return (
    <ol style={listStyle}>
      {steps.map((step, index) => (
        <li key={step.title} style={rowStyle}>
          <span style={indexStyle}>{index + 1}</span>
          <div style={{ display: "grid", gap: nurtDesignTokens.spacing.xs }}>
            <p style={titleStyle}>{step.title}</p>
            <p className="nurt-copy" style={bodyStyle}>
              {step.body}
            </p>
          </div>
        </li>
      ))}
    </ol>
  )
}
