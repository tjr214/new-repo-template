import type { CSSProperties } from "react"

import { nurtDesignTokens } from "@generated/design-tokens"

import { Eyebrow } from "./eyebrow"

export interface HeroPanelProps {
  eyebrow: string
  label: string
  title: string
  body: string
  status: string
}

const panelStyle: CSSProperties = {
  display: "grid",
  gap: nurtDesignTokens.spacing.lg,
  padding: nurtDesignTokens.spacing.xl,
  borderRadius: nurtDesignTokens.radius.lg,
  border: `1px solid ${nurtDesignTokens.colors.border}`,
  background: `linear-gradient(160deg, ${nurtDesignTokens.colors.surface} 0%, ${nurtDesignTokens.colors.surfaceChrome} 100%)`,
  boxShadow: nurtDesignTokens.shadow.strong,
}

const headerStyle: CSSProperties = {
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  gap: nurtDesignTokens.spacing.md,
  flexWrap: "wrap",
}

const labelStyle: CSSProperties = {
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

const titleStyle: CSSProperties = {
  margin: 0,
  fontFamily: nurtDesignTokens.typography.display,
  fontSize: "clamp(2.4rem, 5vw, 4.75rem)",
  lineHeight: 1,
}

const bodyStyle: CSSProperties = {
  margin: 0,
  maxWidth: "34rem",
  color: nurtDesignTokens.colors.mutedForeground,
  fontSize: "1.02rem",
  lineHeight: 1.7,
}

const statusStyle: CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  gap: nurtDesignTokens.spacing.xs,
  width: "fit-content",
  padding: `${nurtDesignTokens.spacing.xs} ${nurtDesignTokens.spacing.sm}`,
  borderRadius: nurtDesignTokens.radius.pill,
  backgroundColor: nurtDesignTokens.colors.surfaceRaised,
  border: `1px solid ${nurtDesignTokens.colors.border}`,
  color: nurtDesignTokens.colors.foreground,
}

const statusDotStyle: CSSProperties = {
  width: "0.55rem",
  height: "0.55rem",
  borderRadius: nurtDesignTokens.radius.pill,
  backgroundColor: nurtDesignTokens.colors.accent,
}

export function HeroPanel({ eyebrow, label, title, body, status }: HeroPanelProps) {
  return (
    <section style={panelStyle}>
      <div style={headerStyle}>
        <Eyebrow>{eyebrow}</Eyebrow>
        <span style={labelStyle}>{label}</span>
      </div>
      <div style={{ display: "grid", gap: nurtDesignTokens.spacing.md }}>
        <h1 style={titleStyle}>{title}</h1>
        <p className="nurt-copy" style={bodyStyle}>
          {body}
        </p>
      </div>
      <div style={statusStyle}>
        <span style={statusDotStyle} />
        <span>{status}</span>
      </div>
    </section>
  )
}
