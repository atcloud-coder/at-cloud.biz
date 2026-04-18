# at-cloud.biz

Repository for the **@Cloud** public site: a tracked **WordPress static mirror**, a **hand-maintained static HTML** tree, and **standalone landing pages**.

## WordPress mirror (`design/at-cloud.biz/`)

A wget-style static copy of the live WordPress site (HTML, `wp-content`, etc.) lives under **`design/at-cloud.biz/`**. It is large and is **tracked in git** in this repo.

Preview locally:

```bash
cd design/at-cloud.biz && python3 -m http.server 8765
```

Open `http://127.0.0.1:8765/`.

If you want to **stop showing ignored folders** in the file explorer (for example after you ignore parts of `design/` locally), open Settings and adjust **Explorer: Exclude Git Ignore** (`explorer.excludeGitIgnore`). There is a commented-out `# design/` line in **`.gitignore`** you can use as a starting point if you need to keep a refreshed mirror out of commits or out of the explorer.

## Clean static site (`docs/`)

The plain HTML/CSS/vanilla JS version of the **core** public pages (no WordPress theme) lives under **`docs/`**. This replaces the former **`design-clean/`** layout.

Preview locally:

```bash
cd docs && python3 -m http.server 8765
```

Open `http://127.0.0.1:8765/`.

Notable paths:

- Top-level pages: `index.html`, `about.html`, `leadership.html`, `mentors.html`, `emba.html`, `events.html`, `donation.html`, `contact.html`
- Program pages: `programs/*.html` (for example EMBA mentor circles, NextGen coaching and internship)
- Event details: `events/*.html`
- Shared assets: `assets/css/`, `assets/js/`, `assets/images/`

More notes live in **`docs/README.md`**.

## Landing pages (`landing_pages/`)

Campaign-style single-file landings live at the repo root under **`landing_pages/`** (`EMBA_Landing.html`, `NextGen_Internship.html`, `NextGen_Mentorship.html`). The same files are also kept under **`design/landing_pages/`** next to the mirror.

Preview from the repo root:

```bash
cd landing_pages && python3 -m http.server 8765
```
