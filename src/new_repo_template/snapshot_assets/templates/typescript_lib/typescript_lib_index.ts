export interface LibrarySummary {
  title: string;
  body: string;
}

export function buildLibraryMessage(subject: string): LibrarySummary {
  const normalizedSubject = subject.trim() || "workspace builder";

  return {
    title: "TypeScript Library Starter",
    body: `Hello, ${normalizedSubject}! This reusable package lives in packages/typescript.`,
  };
}
