import { chromium } from "playwright";
import { mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const output = path.join(root, "docs", "demo_screenshots");
await mkdir(output, { recursive: true });
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
await page.goto("http://localhost:8088", { waitUntil: "networkidle" });
await page.screenshot({ path: path.join(output, "01-start.png"), fullPage: false });

const first = page.locator("ol.recordings button").first();
await first.waitFor();
await first.click();
await page.locator("section[aria-labelledby='timeline-title']").waitFor().catch(() => {});
await page.waitForTimeout(500);
await page.screenshot({ path: path.join(output, "02-timeline.png"), fullPage: false });

const question = page.locator("input.question");
await question.fill("Có tiếng chim trước tiếng còi xe không?");
await question.press("Enter");
await page.locator(".parsed-filters").waitFor({ timeout: 30000 });
await page.screenshot({ path: path.join(output, "03-filter-chip.png"), fullPage: false });
const run = page.locator(".parsed-filters button.primary");
await run.click();
await page.locator(".answer").waitFor({ timeout: 30000 });
await page.screenshot({ path: path.join(output, "04-rag-evidence.png"), fullPage: false });
await browser.close();
console.log(`Đã chụp 4 ảnh fallback tại ${output}`);
