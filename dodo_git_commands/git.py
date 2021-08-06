from dodo_commands import Dodo
from dodo_commands.framework.util import to_arg_list


def _args():
    Dodo.parser.add_argument("git_args", nargs="?")
    args = Dodo.parse_args()
    return args


if Dodo.is_main(__name__):
    args = _args()
    Dodo.run(
        [
            "git",
        ]
        + to_arg_list(args.git_args),
        cwd=Dodo.get_config("/ROOT/src_dir"),
    )
