# @Cloud — clean static HTML

Plain HTML/CSS/vanilla JS rebuild of the core public pages (no WordPress, Elementor, or theme assets).

## Preview locally

```bash
cd design-clean
python3 -m http.server 8765
```

Open <http://127.0.0.1:8765/>

## Structure

- Root HTML pages: `index.html`, `about.html`, `leadership.html`, `mentors.html`, `emba.html`, `events.html`, `donation.html`, `contact.html`
- Event details: `events/*.html`
- Assets: `assets/css/`, `assets/js/`, `assets/images/`

## Notes

- The contact form is a static preview: submit is handled in `assets/js/main.js` with a short message (hook up to your backend or `mailto:` flow separately).
- Images were copied from the `design/at-cloud.biz` mirror where available. Event detail copy matches the mirrored single-event HTML (`index.html?p=…`); the slug folders under `design/at-cloud.biz/events/*` in the wget mirror did not contain standalone pages, so those pages were rebuilt from that content.
- The “More past seminars” section on `events.html` uses YouTube thumbnail images (no WordPress asset paths).
