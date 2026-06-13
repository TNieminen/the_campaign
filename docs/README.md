Great Northwood — DM Toolkit (web)
==================================

A static, browser-based UI for the Great Northwood travel tools. It runs the
**real** `encounter.py` and `loot.py` logic client-side via
[PyScript](https://pyscript.net) (Python compiled to WebAssembly), so there is
no server to run or pay for. Hosted with **GitHub Pages**.

What's inside:

- **Encounters** — build monster encounters (and see matching environmental
  challenges) for a party, using the 2024 XP-budget rules.
- **Loot & Discovery** — enter the players' travel d20 and roll loot; a natural
  20 also rolls a guardian (none / hazard / boss-tier monster).
- **Bestiary** — browse every monster stat block.
- **Reference** — the loot tables and environmental hazards.

## Files

| File | Purpose |
| --- | --- |
| `index.html` | Page shell, login gate, tab logic. |
| `app.py` | PyScript app; imports `encounter`/`loot` and builds the UI. |
| `styles.css` | Theme. |
| `pyscript.json` | PyScript config (which files to load into the browser FS). |
| `data.json` | **Generated** content bundle (monsters, environments, loot). |
| `encounter.py`, `loot.py` | **Generated** copies of the tool modules. |
| `build_data.py` | Regenerates `data.json` and the tool copies from the notes. |

`data.json`, `encounter.py`, and `loot.py` are build artifacts — the source of
truth stays the markdown under `notes/dnd/greath-northwood/`.

## Regenerate after editing the notes

Whenever you change monsters, environments, loot, or the tool scripts:

```
python3 docs/build_data.py
```

Then commit the updated `docs/` files.

## Preview locally

PyScript must be served over HTTP (not opened as a `file://`):

```
python3 -m http.server --directory docs 8000
# open http://localhost:8000
```

## Deploy on GitHub Pages (one-time setup)

The site is committed under `docs/` on `main`. To publish it:

1. On GitHub, open the repo → **Settings** → **Pages**.
2. Under **Build and deployment**, set **Source** to **Deploy from a branch**.
3. Choose branch **`main`** and folder **`/docs`**, then **Save**.
4. Wait ~1 minute; the site appears at
   `https://<your-username>.github.io/the_campaign/`.

## Login

- **Username:** `Pridonia`
- **Password:** `frostfang`

> **Security note — please read.** This login is a *cosmetic deterrent only*.
> Everything needed to bypass it (this page, `data.json`, and the `.py` files)
> is downloadable by anyone who has the URL, and the password check runs in the
> browser. Do not put anything sensitive here, and assume the published content
> is effectively public. To change the password, replace `PASS_HASH` in
> `index.html` with the SHA-256 hex of your new password:
>
> ```
> python3 -c "import hashlib; print(hashlib.sha256(b'YOUR_PASSWORD').hexdigest())"
> ```
>
> If the repository is **public**, its source is browsable on github.com
> regardless of this gate. For real access control you'd need a server-side
> auth layer (out of scope for a static site).
