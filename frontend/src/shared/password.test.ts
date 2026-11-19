import { describe, expect, it } from "vitest";
import { passwordChecks } from "./password";

describe("new user password rules", () => {
  it("accepts a strong password that differs from the username", () => {
    expect(passwordChecks("StrongPass123!", "new_hr").every(check => check.valid)).toBe(true);
  });

  it("reports missing character classes", () => {
    const failed = passwordChecks("lowercase", "new_hr").filter(check => !check.valid).map(check => check.label);
    expect(failed).toEqual(["Uppercase letter", "Number", "Symbol"]);
  });

  it("rejects a password containing the username regardless of case", () => {
    const failed = passwordChecks("New_Hr123!", "new_hr").filter(check => !check.valid).map(check => check.label);
    expect(failed).toEqual(["Does not contain username"]);
  });
});
