import { convexClient, crossDomainClient } from "@convex-dev/better-auth/client/plugins"
import { createAuthClient } from "better-auth/react"

// Better Auth client wiring for the provider-neutral web auth boundary.
export const betterAuthEnv = {
  siteUrlEnvVar: "VITE_SITE_URL",
  convexSiteUrlEnvVar: "VITE_CONVEX_SITE_URL",
} as const

export const authClient = createAuthClient({
  baseURL: import.meta.env[betterAuthEnv.convexSiteUrlEnvVar],
  plugins: [crossDomainClient(), convexClient()],
})
