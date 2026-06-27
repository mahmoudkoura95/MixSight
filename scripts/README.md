# scripts/

Operational and development scripts. Anything called from the `Makefile` or root `package.json` `scripts` belongs here once it grows past a one-liner.

Cross-platform: prefer Node.js (`.mjs`) where possible. Use `.sh` only for POSIX-specific operations (Git Bash / WSL on Windows).
