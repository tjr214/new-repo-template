export interface ClerkAuthProviderConfig {
  provider: "clerk"
  publishableKeyEnvVar: "VITE_CLERK_PUBLISHABLE_KEY"
  frontendApiEnvVar: "CLERK_FRONTEND_API_URL"
}

export const authProvider: ClerkAuthProviderConfig = {
  provider: "clerk",
  publishableKeyEnvVar: "VITE_CLERK_PUBLISHABLE_KEY",
  frontendApiEnvVar: "CLERK_FRONTEND_API_URL",
}
