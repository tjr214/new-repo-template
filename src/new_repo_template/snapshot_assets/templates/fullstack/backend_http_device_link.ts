import { httpRouter } from "convex/server"

{{BETTER_AUTH_IMPORTS}}
import {
  handleApproveDeviceLink,
  handleCreateDeviceLink,
  handleGetTvAppSession,
  handleLogoutTvAppSession,
  handleRedeemDeviceLink,
} from "./deviceLink"

const http = httpRouter()

{{BETTER_AUTH_ROUTE_REGISTRATION}}

http.route({
  path: "/device/code",
  method: "POST",
  handler: handleCreateDeviceLink,
})

http.route({
  path: "/device/approve",
  method: "POST",
  handler: handleApproveDeviceLink,
})

http.route({
  path: "/device/token",
  method: "POST",
  handler: handleRedeemDeviceLink,
})

http.route({
  path: "/device/session",
  method: "POST",
  handler: handleGetTvAppSession,
})

http.route({
  path: "/device/logout",
  method: "POST",
  handler: handleLogoutTvAppSession,
})

export const deviceLinkRouteInventory = {
  createCode: "POST /device/code",
  approveCode: "POST /device/approve",
  redeemToken: "POST /device/token",
  readSession: "POST /device/session",
  logoutSession: "POST /device/logout",
} as const

export default http
