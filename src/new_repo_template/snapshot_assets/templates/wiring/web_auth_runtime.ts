import { authMatrix, type RuntimeEnvironment } from "./app-auth"

export function resolveRuntimeEnvironment(): RuntimeEnvironment {
  return import.meta.env.DEV ? "{{DEFAULT_RUNTIME}}" : "prod"
}

export const activeAuthConfig = authMatrix[resolveRuntimeEnvironment()]
