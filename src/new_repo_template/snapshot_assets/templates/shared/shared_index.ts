export const NURT_FRONTEND_COPY = {
  eyebrow: "Welcome To Nurt",
  title: "Your generated app baseline is ready.",
  body: "This repo starts with target-specific apps, shared packages, and repo-level tooling so you can build on a working nurt baseline instead of starting from zero.",
  highlightsHeading: "What You Have",
  gettingStartedHeading: "How To Build Here",
  caption: "The baseline stays shared in intent while each target keeps its own runtime, layout, and input model.",
  primaryAction: "Start Building",
  secondaryAction: "Explore The Scaffold",
} as const

export const NURT_WELCOME_HIGHLIGHTS = [
  {
    title: "Shared foundations already wired",
    body: "Shared packages carry copy, tokens, and reusable code without flattening the real differences between platforms.",
  },
  {
    title: "Target-specific apps stay native",
    body: "Web, desktop, mobile, and TV each keep their own runtime and interaction model where it matters.",
  },
  {
    title: "Ready for real product work",
    body: "Use this baseline to add product behavior, auth flows, backend logic, and platform-specific polish.",
  },
] as const

export const NURT_GETTING_STARTED_STEPS = [
  "Work from the repo root when running the monorepo.",
  "Build product behavior inside the target apps and reusable packages.",
  "Use the scaffolded docs and commands as the starting workflow, then shape them around your product.",
] as const

export const NURT_TV_WELCOME_CARDS = [
  {
    title: "Start Building",
    body: "Open the target app lanes, follow the starter guidance, and begin replacing this baseline with your product screens.",
  },
  {
    title: "How This Repo Works",
    body: "Nurt gives you a monorepo with target-specific apps plus shared packages so you can evolve the product without starting from scratch.",
  },
  {
    title: "Shared Foundations",
    body: "Copy, tokens, and reusable code can stay shared while each platform keeps its own rendering and input behavior.",
  },
] as const

export const NURT_WELCOME_MESSAGE = NURT_FRONTEND_COPY.title

export const NURT_ROUTE_INTENTS = {
  home: "/",
} as const
