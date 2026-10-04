"""React to closed marker files without repeatedly polling GPU jobs."""
import ctypes,json,os,select
from pathlib import Path


def valid_json(path):
    try:json.loads(Path(path).read_text());return True
    except (FileNotFoundError,json.JSONDecodeError,UnicodeDecodeError):return False


def wait_for_marker(target,failures):
    target=Path(target);failures=[Path(p) for p in failures]
    libc=ctypes.CDLL(None,use_errno=True)
    libc.inotify_init1.argtypes=[ctypes.c_int];libc.inotify_init1.restype=ctypes.c_int
    libc.inotify_add_watch.argtypes=[ctypes.c_int,ctypes.c_char_p,ctypes.c_uint32]
    libc.inotify_add_watch.restype=ctypes.c_int
    fd=libc.inotify_init1(os.O_CLOEXEC)
    if fd<0:raise OSError(ctypes.get_errno(),'inotify_init1')
    try:
        for parent in {p.parent for p in [target,*failures]}:
            if libc.inotify_add_watch(fd,os.fsencode(parent),0x00000008|0x00000080)<0:
                raise OSError(ctypes.get_errno(),f'inotify_add_watch {parent}')
        while True:
            for failed in failures:
                if valid_json(failed):raise RuntimeError(f'Preceding stage failed: {failed}')
            if valid_json(target):return
            ready,_,_=select.select([fd],[],[],900)
            if ready:os.read(fd,65536)
    finally:os.close(fd)
