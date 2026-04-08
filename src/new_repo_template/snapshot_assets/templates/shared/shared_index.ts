export const NURT_WELCOME_HERO = {
  eyebrow: "Welcome To Nurt",
  label: "Operator Console",
  title: "Your generated repo is wired and ready for real product work.",
  body: "Nurt gives you target-specific apps, shared packages, and repo-level tooling so you can move from scaffold to product decisions without rebuilding the foundations first.",
  status: "Shared foundations online",
  caption:
    "The experience stays aligned across targets while each app keeps its own runtime, input model, and platform affordances.",
} as const

export const NURT_WELCOME_ACTIONS = {
  primary: "Start Building",
  secondary: "Explore The Scaffold",
} as const

export const NURT_WELCOME_SECTIONS = {
  highlightsHeading: "Foundations",
  gettingStartedHeading: "Build Path",
  actionsHeading: "Next Moves",
  railHeading: "Console Views",
} as const

export const NURT_FRONTEND_COPY = {
  eyebrow: NURT_WELCOME_HERO.eyebrow,
  title: NURT_WELCOME_HERO.title,
  body: NURT_WELCOME_HERO.body,
  highlightsHeading: NURT_WELCOME_SECTIONS.highlightsHeading,
  gettingStartedHeading: NURT_WELCOME_SECTIONS.gettingStartedHeading,
  caption: NURT_WELCOME_HERO.caption,
  primaryAction: NURT_WELCOME_ACTIONS.primary,
  secondaryAction: NURT_WELCOME_ACTIONS.secondary,
} as const

export const NURT_WELCOME_HIGHLIGHTS = [
  {
    meta: "Shared Layer",
    title: "Packages and tooling are already wired",
    body: "Shared packages carry copy, tokens, and reusable code while the target apps keep ownership of the runtime details that should stay local.",
  },
  {
    meta: "Target Lanes",
    title: "Every frontend keeps its own runtime",
    body: "Web, desktop, mobile, and TV stay aligned in product language without flattening the real differences between browser, Electron, touch, and remote-first surfaces.",
  },
  {
    meta: "Execution",
    title: "The baseline is ready to be replaced with product work",
    body: "Use this starting point to add product behavior, auth flows, backend logic, and platform-specific polish on top of a working repo shape.",
  },
] as const

export const NURT_GETTING_STARTED_STEPS = [
  {
    title: "Start at the repo root",
    body: "Run the monorepo from one place so the app lanes, workspace packages, and tooling stay coordinated from the beginning.",
  },
  {
    title: "Work in the right lane",
    body: "Build product behavior inside the target apps and reusable packages instead of flattening everything into one layer.",
  },
  {
    title: "Use the scaffold as the first draft",
    body: "Keep the docs, commands, and starter UI as the opening move, then reshape them around the product you actually want to ship.",
  },
] as const

export const NURT_TV_WELCOME_CARDS = [
  {
    eyebrow: "Foundations",
    title: "Repo Ready",
    body: "Shared packages, target app lanes, and repo-level tooling are already in place so the team can move directly into product decisions.",
  },
  {
    eyebrow: "Build Path",
    title: "Pick A Lane",
    body: "Move through web, desktop, mobile, and TV with the same product story while keeping rendering, focus, and input behavior local to each target.",
  },
  {
    eyebrow: "Next Moves",
    title: "Ship The Product",
    body: "Replace this console with real flows, wire the app contracts, and keep the shared foundations working for you instead of fighting them.",
  },
] as const

export const NURT_WELCOME_MESSAGE = NURT_WELCOME_HERO.title

export const NURT_ROUTE_INTENTS = {
  home: "/",
} as const
