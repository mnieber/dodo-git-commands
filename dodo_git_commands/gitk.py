from argparse import ArgumentParser

from dodo_commands import Dodo, ConfigArg


def _args():
    parser = ArgumentParser(description='Run gitk')
    args = Dodo.parse_args(parser,
                           config_args=[ConfigArg('/ROOT/src_dir', 'src_dir')])
    return args


# Use safe=False if the script makes changes other than through Dodo.run
if Dodo.is_main(__name__, safe=True):
    args = _args()
    Dodo.run(['gitk'], cwd=args.src_dir)
