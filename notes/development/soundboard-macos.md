# Soundboard on macOS

The Mac app is unsigned. GitHub builds it on a macOS runner and attaches a `.dmg` to a release named **Soundboard macOS** plus the run number. Download that `.dmg` from the release **Assets** list.

Do not install the app from the **soundboard-macos** Actions artifact zip. That zip often breaks the app bundle, and the copy will not open even after the quarantine fix below.

## “Damaged and should be moved to the trash”

macOS Gatekeeper shows this for an unsigned app downloaded from the internet. The file is marked with a quarantine flag. The build is not actually corrupt.

Copy **Soundboard** out of the disk image, then clear the flag in Terminal:

```bash
xattr -cr /Applications/Soundboard.app
```

If the app is still in Downloads, use that path instead. Open the app again after the command finishes.

The first launch of an unsigned app can also be started with a right-click and **Open**. On current macOS that is often not enough until the quarantine flag is removed.

## Library folder

The app reads and writes `config/library.json` inside the selected folder. Audio files live in `audio/` next to `config/`. On a Mac the usual Google Drive location is:

```text
~/Library/CloudStorage/GoogleDrive-*/My Drive/Soundboard/
```

Mark that folder **Available offline** in Drive so tracks start without waiting on a download. Folder names inside the library stay lowercase (`config`, `audio`).
