import type { CSSProperties, ReactNode } from "react"

import { nurtDesignTokens } from "@generated/design-tokens"

import { Eyebrow } from "./eyebrow"

export interface SectionFrameProps {
  heading: string
  label?: string
  children?: ReactNode
}

const frameStyle: CSSProperties = {
  display: "grid",
  gap: nurtDesignTokens.spacing.md,
  padding: nurtDesignTokens.spacing.lg,
  borderRadius: nurtDesignTokens.radius.lg,
  border: `1px solid ${nurtDesignTokens.colors.border}`,
  backgroundColor: nurtDesignTokens.colors.surface,
  boxShadow: nurtDesignTokens.shadow.glow,
}

const headingStyle: CSSProperties = {
  margin: 0,
  fontFamily: nurtDesignTokens.typography.display,
  fontSize: "1.15rem",
}

export function SectionFrame({ heading, label, children }: SectionFrameProps) {
  return (
    <section style={frameStyle}>
      <div style={{ display: "grid", gap: nurtDesignTokens.spacing.xs }}>
        {label ? <Eyebrow tone="muted">{label}</Eyebrow> : null}
        <h2 style={headingStyle}>{heading}</h2>
      </div>
      {children}
    </section>
  )
}
