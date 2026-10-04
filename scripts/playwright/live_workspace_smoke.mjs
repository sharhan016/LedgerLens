import { chromium } from "../../frontend/node_modules/@playwright/test/index.mjs";

const consoleErrors = [];
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
page.on("console", (message) => {
  if (message.type() === "error") consoleErrors.push(message.text());
});

await page.goto("http://127.0.0.1:5173", { waitUntil: "networkidle" });
await page.getByRole("button", { name: /Mira Fernandes/ }).click();
await page.getByLabel("Question for the authorized knowledge base").fill(
  "What is the minimum balance for the Premium Savings Account?",
);
await page.getByRole("button", { name: "Generate cited answer" }).click();
await page.getByText(/Semantic cache|demo-extractive-not-llm/i).waitFor();
await page.getByText(/INR 25,000/).waitFor();
await page.getByRole("button", { name: /S1 Premium Savings Account Policy/ }).click();
await page.getByText("premium-savings-policy.md").waitFor();
await page.screenshot({ path: "/tmp/ledgerlens-live-stack.png", fullPage: true });
if (consoleErrors.length) throw new Error(`Browser console errors: ${consoleErrors.join("\n")}`);
await browser.close();
console.log("live workspace smoke passed; screenshot: /tmp/ledgerlens-live-stack.png");
