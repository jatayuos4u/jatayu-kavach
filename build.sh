#!/bin/sh
set -eu
cd "$(dirname "$0")"
output_dir=${1:-.}
mkdir -p "$output_dir"
stage=$(mktemp -d)
trap 'rm -rf "$stage"' EXIT HUP INT TERM
pkg="$stage/package"
base="$pkg/usr"
install -d "$pkg/DEBIAN" "$base/bin" "$base/share/jatayu-kavach" \
    "$base/share/applications" "$base/share/icons/hicolor/64x64/apps" \
    "$base/share/doc/jatayu-kavach"
install -m644 packaging/control "$pkg/DEBIAN/control"
version=$(sed -n 's/^Version: //p' packaging/control)
printf '%s\n' "$version" > "$base/share/jatayu-kavach/version.txt"
install -m755 packaging/jatayu-kavach "$base/bin/jatayu-kavach"
install -m644 launcher.py content.json kavach.png LICENSE "$base/share/jatayu-kavach/"
install -d "$base/share/jatayu-kavach/locales" "$base/share/jatayu-kavach/learn-art"
install -m644 locales/*.json "$base/share/jatayu-kavach/locales/"
python3 packaging/validate-catalogs.py "$base/share/jatayu-kavach"
install -m644 learn-art/*.png "$base/share/jatayu-kavach/learn-art/"
install -m644 packaging/org.jatayu.kavach.standalone.desktop "$base/share/applications/"
install -m644 kavach.png "$base/share/icons/hicolor/64x64/apps/org.jatayu.kavach.standalone.png"
install -m644 packaging/copyright UPSTREAM-COPYRIGHT.md "$base/share/doc/jatayu-kavach/"
gzip -n -9 -c packaging/changelog > "$base/share/doc/jatayu-kavach/changelog.Debian.gz"
(
    cd "$pkg"
    find usr -type f -print0 | sort -z | xargs -0 md5sum > DEBIAN/md5sums
)
dpkg-deb --root-owner-group --build "$pkg" "$output_dir/jatayu-kavach_${version}_all.deb"
