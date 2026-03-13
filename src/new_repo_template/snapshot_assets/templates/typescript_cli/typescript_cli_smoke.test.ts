import { expect, test } from "bun:test";

import { buildSummary } from "./src/index";

test("buildSummary keeps the requested subject", () => {
  const summary = buildSummary("demo-user");

  expect(summary.body).toContain("demo-user");
  expect(summary.commands[0]).toBe("bun run dev -- --help");
});
