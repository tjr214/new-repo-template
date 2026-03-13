#!/usr/bin/env bun

import { buildSummary, renderSummary } from "./index";

function printHelp(): void {
  console.log(`TypeScript CLI starter

Usage:
  typescript-cli [subject]
  typescript-cli --help`);
}

const args = process.argv.slice(2);

if (args.includes("--help") || args.includes("-h")) {
  printHelp();
  process.exit(0);
}

console.log(renderSummary(buildSummary(args.join(" "))));
