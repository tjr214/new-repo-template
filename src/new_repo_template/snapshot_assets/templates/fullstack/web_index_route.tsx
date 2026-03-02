import { createFileRoute } from "@tanstack/react-router"

import { NURT_WELCOME_MESSAGE } from "@generated/shared"

export const Route = createFileRoute("/")({
  component: HomePage,
})

function HomePage() {
  return <main>{NURT_WELCOME_MESSAGE}</main>
}
