export interface NurtColorTokens {
  background: string
  surface: string
  surfaceRaised: string
  border: string
  accent: string
  accentMuted: string
  foreground: string
  mutedForeground: string
}

export interface NurtSpacingTokens {
  xs: string
  sm: string
  md: string
  lg: string
  xl: string
}

export interface NurtRadiusTokens {
  sm: string
  md: string
  lg: string
  pill: string
}

export interface NurtTypographyTokens {
  body: string
  display: string
  mono: string
}

export interface NurtDesignTokens {
  colors: NurtColorTokens
  spacing: NurtSpacingTokens
  radius: NurtRadiusTokens
  typography: NurtTypographyTokens
  shadow: {
    soft: string
    strong: string
  }
}

export const nurtDesignTokens: NurtDesignTokens = {
  colors: {
    background: "#071521",
    surface: "#102538",
    surfaceRaised: "#17314a",
    border: "#2e516e",
    accent: "#78e7d5",
    accentMuted: "#c6fff6",
    foreground: "#eff8fb",
    mutedForeground: "#a5c0d1",
  },
  spacing: {
    xs: "0.5rem",
    sm: "0.75rem",
    md: "1rem",
    lg: "1.5rem",
    xl: "2rem",
  },
  radius: {
    sm: "0.5rem",
    md: "0.875rem",
    lg: "1.25rem",
    pill: "999px",
  },
  typography: {
    body: 'Inter, "Segoe UI", system-ui, sans-serif',
    display: 'Space Grotesk, "Segoe UI", system-ui, sans-serif',
    mono: '"SFMono-Regular", "SF Mono", Consolas, monospace',
  },
  shadow: {
    soft: "0 18px 48px rgba(0, 0, 0, 0.18)",
    strong: "0 28px 70px rgba(0, 0, 0, 0.32)",
  },
}
