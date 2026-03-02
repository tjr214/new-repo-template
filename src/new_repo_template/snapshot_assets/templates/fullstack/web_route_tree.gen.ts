import { Route as rootRoute } from "./routes/__root"
import { Route as indexRoute } from "./routes/index"

const indexRouteWithParent = indexRoute.update({
  getParentRoute: () => rootRoute,
} as never)

export const routeTree = rootRoute.addChildren([indexRouteWithParent])
