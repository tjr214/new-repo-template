export type DeviceLinkStatus =
  | "authorization_pending"
  | "slow_down"
  | "access_denied"
  | "expired_token"
  | "invalid_grant"
  | "invalid_request"
  | "linked"

export interface DeviceLinkRecord {
  deviceCode: string
  userCode: string
  verificationUri: string
  verificationUriComplete: string
  status: DeviceLinkStatus
  expiresAt: string
  intervalSeconds: number
  approvedUserId?: string
  redeemedSessionToken?: string
}

export interface CreateDeviceLinkResponse {
  device_code: string
  user_code: string
  verification_uri: string
  verification_uri_complete: string
  expires_in: number
  interval: number
}

export const SAMPLE_DEVICE_LINK_RESPONSE: CreateDeviceLinkResponse = {
  device_code: "tv-device-code-sample",
  user_code: "NURT-1400",
  verification_uri: "http://localhost:3000/device",
  verification_uri_complete: "http://localhost:3000/device?user_code=NURT-1400",
  expires_in: 600,
  interval: 5,
}

export const DEVICE_LINK_ROUTE_INVENTORY = {
  createCode: "POST /device/code",
  approveCode: "POST /device/approve",
  redeemToken: "POST /device/token",
} as const

export const DEVICE_LINK_STATUS_HINTS: Record<DeviceLinkStatus, string> = {
  authorization_pending: "Keep polling until the signed-in web user approves the request.",
  slow_down: "Back off polling and retry at a slower interval.",
  access_denied: "Stop polling and show a denied state on the TV.",
  expired_token: "Stop polling and issue a new device-link session.",
  invalid_grant: "Treat the current code as invalid and restart the flow.",
  invalid_request: "Fix the request payload before retrying.",
  linked: "Redeem the approved link into an app-level TV session/token.",
}
