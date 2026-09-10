# Automation safety notes

NOVA can interact with desktop and browser controls, so automation commands should be treated as potentially state-changing operations.

## Recommended behavior

- Prefer explicit confirmation before destructive or irreversible actions.
- Keep sensitive credentials out of command arguments and logs.
- Validate targets before acting on windows, files, or external services.
- Report failures clearly instead of silently retrying state-changing operations.
- Keep permission checks close to the operation they protect.

## Testing

Exercise automation features with harmless local targets first. Tests should verify both successful commands and denied or invalid requests.