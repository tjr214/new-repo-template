import { NURT_WELCOME_MESSAGE } from "@generated/shared"

const rootElement = document.getElementById("app-root")

if (rootElement !== null) {
  rootElement.textContent = NURT_WELCOME_MESSAGE
}
