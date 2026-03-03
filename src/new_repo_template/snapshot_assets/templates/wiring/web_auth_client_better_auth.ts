export interface BetterAuthClientConfig {
  provider: "better auth"
  endpoint: "/api/auth"
  siteUrlEnvVar: "VITE_SITE_URL"
}

export const authClient: BetterAuthClientConfig = {
  provider: "better auth",
  endpoint: "/api/auth",
  siteUrlEnvVar: "VITE_SITE_URL",
}
