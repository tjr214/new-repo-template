import type { ReactNode } from "react"
import { Fragment, createElement } from "react"

import { ClerkProvider } from "@clerk/tanstack-react-start"

import { activeAuthConfig } from "./auth-runtime"

const publishableKeys = {
  local: import.meta.env.VITE_CLERK_PUBLISHABLE_KEY_LOCAL,
  prod: import.meta.env.VITE_CLERK_PUBLISHABLE_KEY_PROD,
} as const

export function AppAuthProvider({ children }: { children: ReactNode }) {
  if (activeAuthConfig.provider !== "clerk") {
    return createElement(Fragment, null, children)
  }

  const publishableKey = publishableKeys[activeAuthConfig.runtime]
  if (!publishableKey) {
    return createElement(Fragment, null, children)
  }

  return createElement(ClerkProvider, { publishableKey }, children)
}
