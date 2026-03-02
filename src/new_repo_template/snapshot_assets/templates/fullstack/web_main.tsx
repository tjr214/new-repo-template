import { StrictMode } from "react"
import { createRoot } from "react-dom/client"
import { RouterProvider } from "@tanstack/react-router"

import { router } from "./router"
import "./styles.css"

const rootElement = document.getElementById("app")

if (rootElement === null) {
  throw new Error("Missing #app mount node for TanStack Start app")
}

createRoot(rootElement).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
)
