import type { AuthConfig } from "convex/server"
import { getAuthConfigProvider } from "@convex-dev/better-auth/auth-config"

type RuntimeEnvironment = "local" | "prod"
type AuthProvider = "clerk" | "better-auth"

const runtimeEnvironment: RuntimeEnvironment =
  process.env.NURT_RUNTIME_ENV === "prod" ? "prod" : "local"

const authMatrix: Record<RuntimeEnvironment, AuthProvider> = {
  local: "{{LOCAL_AUTH_PROVIDER}}",
  prod: "{{PROD_AUTH_PROVIDER}}",
}

const clerkIssuerDomainByRuntime: Record<RuntimeEnvironment, string | undefined> = {
  local: process.env.CLERK_JWT_ISSUER_DOMAIN_LOCAL,
  prod: process.env.CLERK_JWT_ISSUER_DOMAIN_PROD,
}

const selectedProvider = authMatrix[runtimeEnvironment]

export default {
  providers: [
    selectedProvider === "better-auth"
      ? getAuthConfigProvider()
      : {
          domain: clerkIssuerDomainByRuntime[runtimeEnvironment]!,
          applicationID: "convex",
        },
  ],
} satisfies AuthConfig
