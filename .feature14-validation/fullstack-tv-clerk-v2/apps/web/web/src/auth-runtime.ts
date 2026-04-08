import { authMatrix, type RuntimeEnvironment } from "./app-auth"

export function resolveRuntimeEnvironment(): RuntimeEnvironment {
  return import.meta.env.DEV ? "local" : "prod"
}

export const activeAuthConfig = authMatrix[resolveRuntimeEnvironment()]
