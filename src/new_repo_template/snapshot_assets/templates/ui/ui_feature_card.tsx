import type { CSSProperties } from "react"

import { nurtDesignTokens } from "@generated/design-tokens"

import { Eyebrow } from "./eyebrow"

export interface FeatureCardProps {
  meta: string
  title: string
  body: string
}

const cardStyle: CSSProperties = {
  display: "grid",
  gap: nurtDesignTokens.spacing.sm,
  padding: nurtDesignTokens.spacing.md,
  borderRadius: nurtDesignTokens.radius.md,
  border: `1px solid ${nurtDesignTokens.colors.border}`,
  backgroundColor: nurtDesignTokens.colors.surfaceRaised,
}

const titleStyle: CSSProperties = {
  margin: 0,
  fontSize: "1rem",
  fontWeight: 650,
}

const bodyStyle: CSSProperties = {
  margin: 0,
  color: nurtDesignTokens.colors.mutedForeground,
}

export function FeatureCard({ meta, title, body }: FeatureCardProps) {
  return (
    <article style={cardStyle}>
      <Eyebrow tone="muted">{meta}</Eyebrow>
      <p style={titleStyle}>{title}</p>
      <p className="nurt-copy" style={bodyStyle}>
        {body}
      </p>
    </article>
  )
}
