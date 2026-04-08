import type { CSSProperties, HTMLAttributes, ReactNode } from "react"

import { nurtDesignTokens } from "@generated/design-tokens"

import { cn } from "../lib/utils"

export interface EyebrowProps extends HTMLAttributes<HTMLParagraphElement> {
  children?: ReactNode
  tone?: "accent" | "muted"
}

const baseStyle: CSSProperties = {
  margin: 0,
  fontSize: "0.8rem",
  fontWeight: 700,
  letterSpacing: "0.16em",
  textTransform: "uppercase",
}

const accentStyle: CSSProperties = {
  color: nurtDesignTokens.colors.accent,
}

const mutedStyle: CSSProperties = {
  color: nurtDesignTokens.colors.mutedForeground,
}

export function Eyebrow({
  children,
  className,
  style,
  tone = "accent",
  ...props
}: EyebrowProps) {
  const resolvedToneStyle = tone === "muted" ? mutedStyle : accentStyle

  return (
    <p
      className={cn("nurt-eyebrow", className)}
      style={{ ...baseStyle, ...resolvedToneStyle, ...style }}
      {...props}
    >
      {children}
    </p>
  )
}
