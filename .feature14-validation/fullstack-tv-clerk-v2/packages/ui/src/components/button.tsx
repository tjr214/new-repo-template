import type { ButtonHTMLAttributes, CSSProperties, ReactNode } from "react"

import { nurtDesignTokens } from "@generated/design-tokens"

import { cn } from "../lib/utils"

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children?: ReactNode
  tone?: "primary" | "secondary"
}

const primaryStyle: CSSProperties = {
  appearance: "none",
  border: `1px solid ${nurtDesignTokens.colors.accent}`,
  borderRadius: nurtDesignTokens.radius.pill,
  backgroundColor: nurtDesignTokens.colors.accent,
  color: "#071521",
  cursor: "pointer",
  fontFamily: nurtDesignTokens.typography.body,
  fontSize: "0.95rem",
  fontWeight: 600,
  padding: `${nurtDesignTokens.spacing.sm} ${nurtDesignTokens.spacing.lg}`,
}

const secondaryStyle: CSSProperties = {
  ...primaryStyle,
  backgroundColor: nurtDesignTokens.colors.surfaceRaised,
  border: `1px solid ${nurtDesignTokens.colors.border}`,
  color: nurtDesignTokens.colors.foreground,
}

export function Button({
  className,
  style,
  tone = "primary",
  type = "button",
  ...props
}: ButtonProps) {
  const resolvedStyle = tone === "secondary" ? secondaryStyle : primaryStyle

  return (
    <button
      type={type}
      className={cn("nurt-button", className)}
      style={{ ...resolvedStyle, ...style }}
      {...props}
    />
  )
}
