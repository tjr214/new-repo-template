import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const wrapperPath = join(
  process.cwd(),
  "android",
  "gradle",
  "wrapper",
  "gradle-wrapper.properties",
);

const targetDistributionUrl =
  "distributionUrl=https\\://services.gradle.org/distributions/gradle-8.14.3-bin.zip";

if (!existsSync(wrapperPath)) {
  console.error(
    `[tv:android:wrapper:patch] missing ${wrapperPath}; run \`expo prebuild --clean --platform android\` first.`,
  );
  process.exit(1);
}

const currentContent = readFileSync(wrapperPath, "utf-8");
const replacedContent = currentContent.replace(
  /distributionUrl=https\\:\/\/services\.gradle\.org\/distributions\/gradle-[^-\n]+-bin\.zip/,
  targetDistributionUrl,
);

if (replacedContent === currentContent) {
  if (currentContent.includes("gradle-8.14.3-bin.zip")) {
    console.log(
      "[tv:android:wrapper:patch] Gradle wrapper already pinned to 8.14.3.",
    );
    process.exit(0);
  }

  console.error(
    "[tv:android:wrapper:patch] could not locate Gradle distributionUrl in gradle-wrapper.properties.",
  );
  process.exit(1);
}

writeFileSync(wrapperPath, replacedContent, "utf-8");
console.log("[tv:android:wrapper:patch] Pinned Android Gradle wrapper to 8.14.3.");
