from argparse import ArgumentParser
import os

from plumbum.cmd import whoami

from dodo_commands import Dodo


def _args():
    parser = ArgumentParser()
    args = Dodo.parse_args(parser)
    return args


if Dodo.is_main(__name__):
    args = _args()
    me = whoami()[:-1]
    src_dir = Dodo.get_config("/ROOT/src_dir")
    Dodo.run(
        ["sudo", "chown", "-R",
         "%s:%s" % (me, me),
         os.path.basename(src_dir)],
        cwd=os.path.dirname(src_dir))
