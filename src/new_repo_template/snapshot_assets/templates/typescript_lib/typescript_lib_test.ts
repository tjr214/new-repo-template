import { expect, test } from "bun:test";

import { buildLibraryMessage } from "../src/index";

test("buildLibraryMessage includes the requested subject", () => {
  const summary = buildLibraryMessage("demo-user");

  expect(summary.title).toBe("TypeScript Library Starter");
  expect(summary.body).toContain("demo-user");
});
