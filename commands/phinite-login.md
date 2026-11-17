---
description: "Sign in to Phinite (OAuth, the same login as the Phinite app) or switch workspace"
---
Help the user sign in to Phinite through the `phinite` MCP server.

1. Call `whoami`. If it works, report the user, org, workspace and hours left in one or two lines. If the user asked for
   another workspace, go to step 3.
2. If it fails because the server isn't authenticated, tell the user in three short lines:
   - Run `opencode mcp auth phinite` in a terminal (or open `/mcps` in OpenCode and pick **phinite**).
   - A browser opens on the Phinite login (Google, GitHub or email, as in the app). Pick the org and the workspace to
     build in, then return here.
   - The assistant never sees a password or token. The sign-in ends when its Phinite session expires, or right away
     when they sign out of all sessions in Phinite.
3. To switch workspace, `list_workspaces` shows the choices. A connection works in the workspace picked at sign-in,
   so the user signs in again (`opencode mcp logout phinite`, then `opencode mcp auth phinite`) and picks the other workspace.
4. Call `whoami` again and confirm.
