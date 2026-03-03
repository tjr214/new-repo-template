export type AuthProvider = "clerk" | "better-auth"

interface AuthConfig {
  provider: AuthProvider
  issuerEnvVar: "CLERK_FRONTEND_API_URL" | "SITE_URL"
  tokenAudienceEnvVar: "CONVEX_DEPLOYMENT"
}

const defaultsByProvider: Record<AuthProvider, AuthConfig> = {
  clerk: {
    provider: "clerk",
    issuerEnvVar: "CLERK_FRONTEND_API_URL",
    tokenAudienceEnvVar: "CONVEX_DEPLOYMENT",
  },
  "better-auth": {
    provider: "better-auth",
    issuerEnvVar: "SITE_URL",
    tokenAudienceEnvVar: "CONVEX_DEPLOYMENT",
  },
}

export const authConfig = defaultsByProvider["{{AUTH_PROVIDER}}"]
