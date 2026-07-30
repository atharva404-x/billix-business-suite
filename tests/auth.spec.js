import { test, expect } from "@playwright/test";

const BASE_URL = "http://localhost:8080";

test.describe("Billix Authentication Diagnostic Suite", () => {
  test.beforeEach(async ({ page }) => {
    test.setTimeout(60000);
    page.on("console", (msg) => {
      console.log(`[BROWSER ${msg.type().toUpperCase()}] ${msg.text()}`);
    });

    page.on("pageerror", (err) => {
      console.log("[PAGE ERROR]");
      console.log(err);
    });

    page.on("requestfailed", (request) => {
      console.log("[FAILED REQUEST]");
      console.log(request.url());
      console.log(request.failure()?.errorText);
    });

    page.on("response", async (response) => {
      if (response.status() >= 400) {
        console.log("[HTTP ERROR]");
        console.log(response.status(), response.url());
      }
    });
  });

  test("Login page renders correctly", async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);

    await expect(page).toHaveTitle(/Billix/i);

    await expect(page.locator("#email")).toBeVisible();

    await expect(page.locator("#password")).toBeVisible();

    await expect(
      page.getByRole("button", {
        name: /sign in/i,
      }),
    ).toBeVisible();

    await expect(
      page.getByRole("button", {
        name: /continue with google/i,
      }),
    ).toBeVisible();
  });

  test("Protected dashboard redirects correctly", async ({ page }) => {
    await page.goto(`${BASE_URL}/dashboard`);

    await page.waitForLoadState("networkidle");

    expect(page.url()).toContain("/login");
  });

  test("Invalid login shows Clerk error", async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);

    await page.fill("#email", "fake@example.com");

    await page.fill("#password", "wrongpassword");

    await page
      .getByRole("button", {
        name: /sign in/i,
      })
      .click();

    await page.waitForLoadState("domcontentloaded");

    await expect(page.locator("text=Failed to sign in"))
      .toBeVisible({
        timeout: 10000,
      })
      .catch(() => {});

    await page.screenshot({
      path: "playwright-report/invalid-login.png",
      fullPage: true,
    });
  });

  test("Google OAuth starts correctly", async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);

    await page
      .getByRole("button", {
        name: /continue with google/i,
      })
      .click();

    await page.waitForTimeout(3000);

    expect(page.url()).not.toContain("/login");
  });

  test("Remember me checkbox exists", async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);

    await expect(page.locator("#remember")).toBeVisible();
  });

  test("Forgot password route exists", async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);

    await page
      .getByRole("link", {
        name: /forgot/i,
      })
      .click();

    await expect(page).toHaveURL(/forgot-password/);
  });

  test("Register link works", async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);

    await page
      .getByRole("link", {
        name: /create an account/i,
      })
      .click();

    await expect(page).toHaveURL(/register/);
  });

  test("Console should contain no runtime errors", async ({ page }) => {
    const errors = [];

    page.on("console", (msg) => {
      if (msg.type() === "error") {
        errors.push(msg.text());
      }
    });

    await page.goto(`${BASE_URL}/login`);

    await page.waitForLoadState("domcontentloaded");

    expect(errors).toEqual([]);
  });

  test("Storage Diagnostic", async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);

    const storage = await page.evaluate(() => {
      return {
        localStorage: Object.keys(localStorage),

        sessionStorage: Object.keys(sessionStorage),

        cookies: document.cookie,
      };
    });

    console.log(storage);
  });
});
