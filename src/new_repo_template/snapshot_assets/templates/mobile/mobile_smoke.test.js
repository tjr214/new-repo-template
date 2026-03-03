import { describe, expect, test } from "bun:test";

describe("mobile smoke baseline", () => {
  test("basic assertion", () => {
    expect(1 + 1).toBe(2);
  });
});
