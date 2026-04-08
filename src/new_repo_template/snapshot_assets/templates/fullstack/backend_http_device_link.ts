import { httpRouter } from "convex/server"

const http = httpRouter()

// Feature 14 starter contract: replace this route inventory with real handlers.
export const deviceLinkRouteInventory = {
  createCode: "POST /device/code",
  approveCode: "POST /device/approve",
  redeemToken: "POST /device/token",
} as const

export default http
