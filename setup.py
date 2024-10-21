from py2exe import freeze

freeze(windows=['main.py'], options={'bundle_files': 1})
