[app]
title = Calculador Años Meses Días
package.name = calculador
package.domain = com.example
source.dir = .
source.include_exts = py,png,jpg,kv
version = 0.1
requirements = python3,kivy==2.1.0,num2words
orientation = portrait
entrypoint = kivy_app.py
android.api = 31
android.minapi = 21
android.ndk = 21b
android.arch = armeabi-v7a, arm64-v8a

# Logging
log_level = 2

# Presiona el paquete final en bin/
presplash.filename = presplash.png

[buildozer]
warn_on_root = 1
