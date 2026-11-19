export function passwordChecks(password: string, username: string) {
  return [
    { label: "At least 8 characters", valid: password.length >= 8 },
    { label: "Uppercase letter", valid: /[A-Z]/.test(password) },
    { label: "Lowercase letter", valid: /[a-z]/.test(password) },
    { label: "Number", valid: /[0-9]/.test(password) },
    { label: "Symbol", valid: /[^A-Za-z0-9\s]/.test(password) },
    { label: "Does not contain username", valid: !username || !password.toLowerCase().includes(username.toLowerCase()) },
  ];
}
