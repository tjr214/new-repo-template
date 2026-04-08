import { defineSchema, defineTable } from "convex/server"
import { v } from "convex/values"

export default defineSchema({
  profiles: defineTable({
    userId: v.string(),
    email: v.string(),
  }).index("by_user_id", ["userId"]),
  deviceLinks: defineTable({
    deviceCode: v.string(),
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
    expiresAt: v.string(),
    intervalSeconds: v.number(),
    approvedUserId: v.optional(v.string()),
    redeemedSessionToken: v.optional(v.string()),
  })
    .index("by_device_code", ["deviceCode"])
    .index("by_user_code", ["userCode"]),
})
