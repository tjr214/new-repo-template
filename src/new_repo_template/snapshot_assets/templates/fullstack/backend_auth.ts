import { createClient, type GenericCtx } from "@convex-dev/better-auth"
import { convex } from "@convex-dev/better-auth/plugins"
import { betterAuth, type BetterAuthOptions } from "better-auth"

import authConfig from "./auth.config"
import { components } from "./_generated/api"

export const authComponent = createClient(components.betterAuth)

export function createAuth(ctx: GenericCtx<object>) {
  const options = {
    database: authComponent.adapter(ctx),
    emailAndPassword: {
      enabled: true,
      autoSignIn: true,
    },
    user: {
      additionalFields: {
        displayName: {
          type: "string",
          required: false,
        },
      },
    },
    plugins: [convex({ authConfig })],
  } satisfies BetterAuthOptions

  return betterAuth(options)
}
