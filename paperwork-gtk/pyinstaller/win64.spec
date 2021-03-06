# -*- mode: python -*-

import os
import site
import sys


SIGNTOOL_EXE = "c:\\Program Files\\Microsoft SDKs\\Windows\\v7.1\\Bin\\signtool.exe"
PATH_PFX="c:\\users\\jflesch\\cert\\openpaper.pfx"
PFX_PASSWD="1234"  # Microsoft forced me to put one :p
TIMESTAMP_URL = "http://timestamp.verisign.com/scripts/timestamp.dll"


block_cipher = None

if os.path.exists(os.path.join("src", "launcher.py")):
    BASE_PATH = os.getcwd()
else:
    BASE_PATH = os.path.join(os.path.expanduser("~"), "git", "paperwork", "paperwork-gtk")

# Pyinstaller misses some .dll (GObject & co) --> we have to request them
# explicitly
typelib_path = os.path.join(
    site.getsitepackages()[1], 'gnome', 'lib', 'girepository-1.0'
)
bins = [
    (os.path.join(typelib_path, tl), 'gi_typelibs')
    for tl in os.listdir(typelib_path)
]
lib_path = os.path.join(site.getsitepackages()[1], 'gnome')
extra_libs = [
    (os.path.join(lib_path, 'libpoppler-glib-8.dll'), '.'),
    (os.path.join(lib_path, 'liblcms2-2.dll'), '.'),
    (os.path.join(lib_path, 'libnotify-4.dll'), '.'),
    (os.path.join(lib_path, 'libopenjp2.dll'), '.'),
    (os.path.join(lib_path, 'libstdc++.dll'), '.'),
]
sys.stderr.write("=== Adding extra libs: ===\n{}\n===\n".format(extra_libs))
bins += extra_libs

# We also have to add data files
datas = []
for (dirpath, subdirs, filenames) in os.walk(BASE_PATH):
    shortdirpath = dirpath[len(BASE_PATH):]
    if ("dist" in shortdirpath.lower()
            or "build" in shortdirpath.lower()
            or "egg" in shortdirpath.lower()):
        continue
    for filename in filenames:
        if filename.lower().endswith(".png") and shortdirpath.lower().endswith("doc"):
            continue
        if (not filename.lower().endswith(".ico")
                and not filename.lower().endswith(".png")
                and not filename.lower().endswith(".svg")
                and not filename.lower().endswith(".xml")
                and not filename.lower().endswith(".glade")
                and not filename.lower().endswith(".css")
                and not filename.lower().endswith(".mo")
                and not filename.lower().endswith(".pdf")):
            continue
        filepath = os.path.join(dirpath, filename)

        basename = os.path.basename(dirpath)
        if basename == "frontend" or basename == "data":
            dest = "data"
        elif filename.lower().endswith(".mo"):
            dirpath = os.path.dirname(dirpath)  # drop 'LC_MESSAGES'
            dest = os.path.join("share", "locale", os.path.basename(dirpath), "LC_MESSAGES")
        elif os.path.basename(dirpath) == "doc":
            dest = "data"
        else:
            dest = os.path.join("data", os.path.basename(dirpath))
        sys.stderr.write(
            "=== Adding file [{}] --> [{}] ===\n".format(filepath, dest)
        )
        datas.append((filepath, dest))


a = Analysis(
    [os.path.join(BASE_PATH, 'pyinstaller', 'paperwork_launcher.py')],
    pathex=[],
    binaries=bins,
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,
    name='paperwork',
    debug=False,
    strip=False,
    upx=False,
    console=False,
    icon=os.path.join(BASE_PATH, 'data', 'paperwork_32.ico')
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name='paperwork'
)

if not os.path.exists(PATH_PFX):
    print ("No certifcate for signing")
else:
    import subprocess
    print("Signtool")
    print(SIGNTOOL_EXE)
    print(PATH_PFX)
    print(TIMESTAMP_URL)
    subprocess.call([
        SIGNTOOL_EXE,
        "sign",
        "/F", PATH_PFX,
        "/P", PFX_PASSWD,
        "/T", TIMESTAMP_URL,
        "dist\\paperwork\\paperwork.exe"
    ])
