import type { ReactNode } from "react"
import { Fragment, createElement } from "react"

export function AppAuthProvider({ children }: { children: ReactNode }) {
  return createElement(Fragment, null, children)
}
