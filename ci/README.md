# CI definitions (inactive)

These workflows run SumitCraft's offline checks. They live here, not in `.github/workflows/`, so pushing the
repository does not start anything remotely. To enable them, copy them into `.github/workflows/` yourself.

- `offline-checks.yml`: Ubuntu. Static validation, path unit test, and the functional checks that need no model
  downloads or provider keys.
- `windows-checks.yml`: Windows (windows-2022). Doctor, static validation, path unit test, and the Windows-sensitive
  functional checks. A green run here is what would move Windows rows in the matrix from "not run" to a real status.

Neither workflow uses secrets, downloads speech models or calls paid providers.
