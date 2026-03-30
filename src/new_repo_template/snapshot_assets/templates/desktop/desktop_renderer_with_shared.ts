import { RouterProvider } from "@tanstack/react-router"
import { StrictMode, createElement } from "react"
import { createRoot } from "react-dom/client"

import { getRouter } from "./router"

const rootElement = document.getElementById("app-root")

if (rootElement === null) {
  throw new Error("Desktop app root element was not found")
}

const router = getRouter()

createRoot(rootElement).render(
  createElement(
    StrictMode,
    null,
    createElement(RouterProvider, { router }),
  ),
)
