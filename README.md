# at-cloud.biz
at-cloud public main website

## Static mirror (`design/`)

The wget copy of the public site lives under **`design/at-cloud.biz/`**. The `design/` entry in `.gitignore` keeps it out of git and, in Cursor/VS Code, **hides that folder from the file explorer by default**.

To show it: open Settings and turn off **Explorer: Exclude Git Ignore** (`explorer.excludeGitIgnore`), or temporarily delete the `design/` line from `.gitignore`.

Preview locally: `cd design/at-cloud.biz && python3 -m http.server 8765` then open `http://127.0.0.1:8765/`.
