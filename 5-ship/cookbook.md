# Ship — what bites

| Issue | Fix |
|---|---|
| `resources refresh` reports `Result: Success` and has done nothing | Treat *created 0, imported 0, skipped 0* **with bindings on disk** as a failure, not a no-op. It is the commonest silent step in the whole lifecycle. |
| Publishing rejects the package | The feed refuses a duplicate name and version. Bump the version — never rename the solution. |
| `deploy run --folder-name` puts it somewhere unexpected | It **always creates** a folder, and silently collision-renames when the name is taken. There is no way to deploy into a pre-existing folder. |
| A redeploy leaves a second deployment behind | Same name, higher version — `CONFIG.md`, *Deploying*. Uninstall is recovery, not the loop. |
| `upload --force` loses your version history | It wipes what the designer holds. Know that before you reach for it. |
| The deployed solution runs and the same package fails elsewhere | Something it needs was on your seat rather than in the package. Deploy into a folder that has never held this solution and run a claim there. |
| The app is missing after a deploy that reported success | It is not part of the solution unless it was explicitly added. `3f-validation/cookbook.md`, last row. |

## Promotion is pack once, deploy many

One package, then per environment set the tenant, publish, and deploy with that environment's configuration. **Repacking per environment is how two environments end up running different code with the same version number.**
