interface StartAppConfig {
  name: string
  router: {
    routesDirectory: string
    generatedRouteTree: string
  }
}

const appConfig: StartAppConfig = {
  name: "nurt-web",
  router: {
    routesDirectory: "src/routes",
    generatedRouteTree: "src/routeTree.gen.ts",
  },
}

export default appConfig
