# Guide: Compiling Wealth Tracker to an Android APK

This guide provides step-by-step instructions on how to wrap and compile your Vue/Vite frontend into a native Android Application Package (APK) using **Capacitor** (by Ionic).

---

## 1. Prerequisites (To install on your Windows computer)

Before compiling, you must have the following tools installed and configured on your Windows machine:

1. **Java JDK 17** (or newer)
   - Download from: [Adoptium Temurin](https://adoptium.net/) or Oracle.
   - Ensure the `JAVA_HOME` environment variable is set.
2. **Android Studio**
   - Download from: [Android Studio Official Site](https://developer.android.com/studio).
   - During setup, install the **Android SDK**, **Android SDK Command-line Tools**, and a **Virtual Device (Emulator)**.
3. **Node.js & npm** (already installed).

---

## 2. Set Up Capacitor in the Frontend Project

Run the following commands in your command prompt/terminal under the `frontend` folder:

### Step 2.1: Install Capacitor core and CLI
```bash
npm install @capacitor/core @capacitor/cli
```

### Step 2.2: Initialize Capacitor
```bash
npx cap init "Aether Wealth" "com.aetherwealth.app" --web-dir=dist
```
*Note: Make sure `--web-dir` points to `dist`, as Vite outputs build files into the `dist` directory.*

### Step 2.3: Install the Android Platform
```bash
npm install @capacitor/android
npx cap add android
```

---

## 3. Build & Syncing Assets

Every time you change your frontend code, you must build the web assets and sync them to the Android project:

```bash
# 1. Build the Vite production files
npm run build

# 2. Sync the built files into the Android project
npx cap sync
```

---

## 4. Compile the APK using Android Studio (Recommended)

1. Open **Android Studio**.
2. Select **Open an Existing Project** and choose the `frontend/android` folder in your project directory.
3. Wait for Android Studio to index the project and sync Gradle (this can take a few minutes on the first run).
4. Run/Test the app:
   - Click the **Run** button (green play icon) in the toolbar to run the app in an Android Emulator or on your connected physical Android device.
5. Build the APK:
   - Go to **Build** > **Build Bundle(s) / APK(s)** > **Build APK(s)** in the top menu.
   - Once completed, a pop-up in the bottom right corner will appear. Click **locate** to find your compiled debug APK file (typically named `app-debug.apk`).
