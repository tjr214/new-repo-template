import {
  Outlet,
  createHashHistory,
  createRootRoute,
  createRoute,
  createRouter,
} from "@tanstack/react-router"
import { createElement } from "react"

import { DesktopWelcomePage } from "./app"

const rootRoute = createRootRoute({
  component: RootLayout,
})

function RootLayout() {
  return createElement(Outlet)
}

const homeRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/",
  component: DesktopWelcomePage,
})

const routeTree = rootRoute.addChildren([homeRoute])

export function getRouter() {
  return createRouter({
    routeTree,
    history: createHashHistory(),
    defaultPreload: "intent",
  })
}

declare module "@tanstack/react-router" {
  interface Register {
    router: ReturnType<typeof getRouter>
  }
}
