# Kavach 0.2.2-1 security audit

The review covered the standalone launcher, packaged HTML and JavaScript,
checklist storage, desktop file, and Debian package. Findings were compared
against 0.2.1-1. The work did not audit the JatayuOS ISO, KDE services, or
the underlying Qt WebEngine implementation.

| Finding | Change in 0.2.2-1 |
| --- | --- |
| Broad outbound URL handling | Browser and phone handoff uses an exact allowlist of the app's destinations from the bundled dashboard. The native shortcuts require main-frame link navigation from that dashboard to one of three exact action URLs. The launched programs and arguments are fixed and no shell is invoked. |
| Local page lacked a Content Security Policy | The build hashes its bundled script and stamps a default-deny policy into the HTML. Event handlers are registered by that script. Remote resources, forms, frames, and unapproved scripts are disallowed. External reporting links are handed off to the system. |
| Corrupt checklist storage could break its tab | The app validates the stored array against known checklist IDs, discards duplicates, and recovers from invalid JSON. |
| Rejected navigation could affect the startup screen | The startup listener disconnects after the initial load result. Renderer termination retains its error path. |

## Verification

- The packaged page loaded using Debian 13 Qt WebEngine in an offscreen session.
- All five tabs, the scam detail dialog, and a checklist toggle were exercised.
- Invalid checklist JSON was handled without breaking the checklist.
- Automated checks verified rejection of unrelated external and local URLs,
  subframe phone links and non-link system shortcut requests. Approved handoff
  and shortcut dispatch were checked with mocked process/browser calls.
- The desktop file was validated, package payload checksums matched, and APT
  resolved the package in a Debian 13 installation simulation.
- The live JatayuOS install/upgrade and shortcuts were outside this test setup.

## Release status

Use this build for testing. Debian's trixie release notes say applications
using Qt WebEngine lack Debian security support. The offline content policy and
navigation checks reduce exposure. Moving the dashboard to native Qt Widgets
while preserving the classic layout would remove this dependency before stable
release.

Source: https://www.debian.org/releases/trixie/release-notes/issues.en.html#security-status-of-web-browsers-and-their-rendering-engines

## 0.2.9-1 follow-up audit

Reviewed 0.2.8-1's 28-question expansion, embedded assets, localized strings,
external handoff, native shortcut dispatch, and packaged launcher.

- The exercise search and choice controls use text, and translated content is
  escaped where it passes through an HTML template. Images are packaged WebP
  illustrations. The page-level request policy permits only a GET for the
  bundled dashboard and embedded WebP image requests. External links are
  handled by the desktop handoff, outside the embedded page.
- Deny WebEngine permission requests and cancel page downloads. The installed
  launcher uses Python isolated mode to exclude user-site and PYTHONPATH
  imports. It continues to use the distro-provided PySide6 modules.
- Repair official homepage handoff by using canonical URLs with the trailing
  slash Qt adds. The destination and native command allowlists remain exact.
- Keep keyboard focus when toggling a checklist item. If storage is
  unwritable, keep the state for the current session. Writability is required
  to retain new changes after closing the app.
- Require 1930 to appear as a complete number in the localized emergency label.

Packaged offscreen tests exercised 28 exercises across 23 languages, the six
illustrations, search, topic filters, answer feedback and the Report Crime tab.
Request rules and download cancellation were checked with test doubles.
Real in-app clicks were verified up to the mocked desktop URL handoff and KDE
firewall command. The checklist was exercised with a simulated storage write
failure and keyboard focus was checked. Package ownership, modes, checksums,
desktop metadata and dependency resolution were checked. Live device and KDE
integration testing remains outstanding.

This audit does not independently verify the linguistic accuracy of the
machine-translated guidance. Debian 13's Qt WebEngine security support
limitation remains. Treat 0.2.9-1 as a test build.

## Native preview 0.3.0-1

The application now uses plain-text Qt Widgets for the dashboard, scam details,
checklist and exercises. The binary package has no HTML, Chromium runtime,
WebEngine imports or WebEngine dependencies. Native shortcuts retain fixed
executable and argument lists and external browser handoff retains its exact
allowlist. Language and checklist state are stored in user settings.
This port removes the dependency identified in the earlier audit. It remains
a test build pending live JatayuOS integration and translation review.
