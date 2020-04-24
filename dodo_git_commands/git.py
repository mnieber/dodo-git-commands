from dodo_commands import Dodo


def _args():
    Dodo.parser.add_argument('git_args', nargs="*")
    args = Dodo.parse_args()
    return args


if Dodo.is_main(__name__):
    args = _args()
    Dodo.run(
        [
            "git",
        ] + args.git_args, cwd=Dodo.get_config("/ROOT/src_dir"))
