export interface ClerkAuthProviderConfig {
  provider: "clerk"
  localPublishableKeyEnvVar: "VITE_CLERK_PUBLISHABLE_KEY_LOCAL"
  prodPublishableKeyEnvVar: "VITE_CLERK_PUBLISHABLE_KEY_PROD"
}

export const authProvider: ClerkAuthProviderConfig = {
  provider: "clerk",
  localPublishableKeyEnvVar: "VITE_CLERK_PUBLISHABLE_KEY_LOCAL",
  prodPublishableKeyEnvVar: "VITE_CLERK_PUBLISHABLE_KEY_PROD",
}
