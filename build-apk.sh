#!/usr/bin/env bash
# Builds StickGo.apk from index.html and installs it on a USB-connected phone.
# Usage:  bash build-apk.sh            (build + install + launch)
#         bash build-apk.sh --no-install
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SDK="${ANDROID_HOME:-$LOCALAPPDATA/Android/Sdk}"
BT="$SDK/build-tools/36.0.0"
ANDROID_JAR="$SDK/platforms/android-36/android.jar"
ADB="$SDK/platform-tools/adb.exe"
export JAVA_HOME="${JAVA_HOME_21:-$(ls -d /c/Users/Kim/tools/jdk-21* | head -1)}"
export PATH="$JAVA_HOME/bin:$PATH"

SRC="$ROOT/android"
OUT="$ROOT/build"
KEYSTORE="$SRC/debug.keystore"

rm -rf "$OUT"
mkdir -p "$OUT/assets" "$OUT/gen" "$OUT/classes"
cp "$ROOT/index.html" "$ROOT/animations.js" "$ROOT/hold-data.js" "$OUT/assets/"
mkdir -p "$OUT/assets/pictures"
find "$ROOT/pictures" -maxdepth 1 -type f -exec cp {} "$OUT/assets/pictures/" \;  # originals/ is not packaged
for d in weapons hold icons; do mkdir -p "$OUT/assets/pictures/$d" && cp "$ROOT/pictures/$d/"*.png "$OUT/assets/pictures/$d/"; done

echo "==> Compiling resources"
"$BT/aapt2.exe" compile --dir "$SRC/res" -o "$OUT/res.zip"
"$BT/aapt2.exe" link -o "$OUT/unsigned.apk" -I "$ANDROID_JAR" \
  --manifest "$SRC/AndroidManifest.xml" --java "$OUT/gen" \
  --min-sdk-version 24 --target-sdk-version 35 \
  --version-code 1 --version-name 1.0 \
  "$OUT/res.zip"

echo "==> Compiling Java"
javac -nowarn -source 11 -target 11 -classpath "$ANDROID_JAR" -d "$OUT/classes" \
  $(find "$SRC/src" "$OUT/gen" -name '*.java') 2>&1 | grep -v "bootstrap classpath" || true

echo "==> Converting to dex"
"$BT/d8.bat" --lib "$ANDROID_JAR" --min-api 24 --output "$OUT" $(find "$OUT/classes" -name '*.class')
# Add code + game files. Done here (not via aapt2 -A) because aapt2 on Windows
# stores subfolder paths with backslashes, which Android cannot find.
(cd "$OUT" && "$BT/aapt.exe" add unsigned.apk classes.dex $(find assets -type f) > /dev/null)

echo "==> Aligning and signing"
if [ ! -f "$KEYSTORE" ]; then
  keytool -genkeypair -keystore "$KEYSTORE" -storepass android -keypass android \
    -alias stickgo -keyalg RSA -keysize 2048 -validity 10000 \
    -dname "CN=StickGo Debug" > /dev/null 2>&1
fi
"$BT/zipalign.exe" -p -f 4 "$OUT/unsigned.apk" "$OUT/aligned.apk"
"$BT/apksigner.bat" sign --ks "$KEYSTORE" --ks-pass pass:android \
  --out "$ROOT/StickGo.apk" "$OUT/aligned.apk"
echo "==> Built $ROOT/StickGo.apk"

if [ "${1:-}" != "--no-install" ]; then
  echo "==> Installing on phone"
  "$ADB" install -r "$ROOT/StickGo.apk"
  "$ADB" shell am start -n com.stickgo.game/.MainActivity
fi
