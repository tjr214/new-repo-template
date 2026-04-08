export type AuthProvider = "clerk" | "better-auth"
export type RuntimeEnvironment = "local" | "prod"

export interface RuntimeAuthConfig {
  provider: AuthProvider
  runtime: RuntimeEnvironment
}

export interface AppAuthState {
  provider: AuthProvider
  isLoading: boolean
  isAuthenticated: boolean
  getConvexToken(): Promise<string | null>
}

export const authMatrix: Record<RuntimeEnvironment, RuntimeAuthConfig> = {
  local: {
    provider: "clerk",
    runtime: "local",
  },
  prod: {
    provider: "clerk",
    runtime: "prod",
  },
}
