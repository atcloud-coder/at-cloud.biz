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

## Clean static site (`docs/`) — GitHub Pages

The plain HTML/CSS/vanilla JS version of the **core** public pages (no WordPress theme) lives under **`docs/`**. This replaces the former **`design-clean/`** layout. For **GitHub Pages**, this repo is configured to publish from **`docs/`**, so paths like `docs/index.html` are served as `/index.html` on the site.

Preview locally:

```bash
cd docs && python3 -m http.server 8765
```

Open `http://127.0.0.1:8765/`.

**Sitemap.** Regenerate the list of published HTML paths (site-root paths, one per line) into **`docs/sitemap.txt`** and verify internal links:

```bash
python3 scripts/sitemap_and_linkcheck.py
```

**Search engines** (Google, Bing, and others) expect a sitemap with **full `https://…` URLs**, not bare paths. Submit an **XML** sitemap in Search Console. Generate **`docs/sitemap.xml`** by passing your live site origin (custom domain or `https://<user>.github.io/<repo>/` if the site is not at the domain root):

```bash
python3 scripts/sitemap_and_linkcheck.py --base-url https://at-cloud.biz
```

Then point Search Console at `https://at-cloud.biz/sitemap.xml` (or the matching URL for your host). The plain **`docs/sitemap.txt`** file remains path-only for quick human or script use.

**`docs/robots.txt`** is published as `/robots.txt`. It allows all crawlers (`User-agent: *` / `Allow: /`) and points to the XML sitemap. If the live site uses another host (for example `https://<user>.github.io/<repo>/`), edit the `Sitemap:` line so it matches that origin.

Use `--check-external` if you also want HTTP checks on external `https://` links. The script defaults to scanning **`docs/`** only.

Notable paths:

- Top-level pages: `index.html`, `about.html`, `leadership.html`, `mentors.html`, `emba.html`, `events.html`, `donation.html`, `contact.html`
- About section: `aboutus/index.html`, `aboutus/leadership.html`, `aboutus/mentors.html`
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

## Scripts (`scripts/`)

- **`sitemap_and_linkcheck.py`** — Builds **`docs/sitemap.txt`** (path list) and, with **`--base-url`**, **`docs/sitemap.xml`** for search engines; checks local `href` / `src` targets. Run from the repo root (see above).
- **`rewrite_mirror_urls.py`** — Rewrites absolute `at-cloud.biz` URLs in the WordPress mirror under **`design/at-cloud.biz/`** to root-relative paths for local static serving.
