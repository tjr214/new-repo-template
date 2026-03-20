export interface CliSummary {
  title: string;
  body: string;
  commands: readonly string[];
}

export function buildSummary(subject: string): CliSummary {
  const normalizedSubject = subject.trim() || "terminal builder";

  return {
    title: "TypeScript CLI Starter",
    body: `Hello, ${normalizedSubject}! This Bun-first TypeScript CLI is ready.`,
    commands: [
      "bun run dev -- --help",
      "bun run build",
      "bun run typecheck",
    ],
  };
}

export function renderSummary(summary: CliSummary): string {
  const commandLines = summary.commands.map((command) => `- ${command}`).join("\n");
  return `${summary.body}\n\nStarter commands:\n${commandLines}`;
}
