import { defineSchema, defineTable } from "convex/server"
import { v } from "convex/values"

{{BETTER_AUTH_IMPORTS}}

export default defineSchema({
  {{BETTER_AUTH_TABLES}}
  profiles: defineTable({
    userId: v.string(),
    email: v.string(),
  }).index("by_user_id", ["userId"]),
  deviceLinks: defineTable({
    deviceCode: v.string(),
    clientId: v.string(),
    userCode: v.string(),
    verificationUri: v.string(),
    verificationUriComplete: v.string(),
    status: v.union(
      v.literal("authorization_pending"),
      v.literal("slow_down"),
      v.literal("access_denied"),
      v.literal("expired_token"),
      v.literal("invalid_grant"),
      v.literal("invalid_request"),
      v.literal("linked")
    ),
    expiresAtMs: v.number(),
    intervalSeconds: v.number(),
    lastPolledAtMs: v.optional(v.number()),
    approvedUserId: v.optional(v.string()),
    approvedAtMs: v.optional(v.number()),
    linkedSessionToken: v.optional(v.string()),
    linkedAtMs: v.optional(v.number()),
  })
    .index("by_device_code", ["deviceCode"])
    .index("by_user_code", ["userCode"]),
  tvSessions: defineTable({
    sessionToken: v.string(),
    userId: v.string(),
    deviceCode: v.string(),
    clientId: v.string(),
    createdAtMs: v.number(),
    expiresAtMs: v.number(),
    revokedAtMs: v.optional(v.number()),
  })
    .index("by_session_token", ["sessionToken"])
    .index("by_user_id", ["userId"]),
})
