import { createRoute } from "@tanstack/react-router"

import { Route as rootRoute } from "./__root"

import { NURT_WELCOME_MESSAGE } from "@generated/shared"

export const Route = createRoute({
  getParentRoute: () => rootRoute,
  path: "/",
  component: HomePage,
})

function HomePage() {
  return <main>{NURT_WELCOME_MESSAGE}</main>
}
