import os
import glob
from collections import defaultdict
from argparse import ArgumentParser

from dodo_commands import Dodo, ConfigArg, CommandError
from dodo_commands.framework.command_path import get_command_dirs_from_config

prefixes = ('pre-commit', )


def _all_hooks():
    command_dirs = get_command_dirs_from_config(Dodo.get_config())
    result = defaultdict(lambda: {})
    for command_dir in command_dirs:
        hooks_path = os.path.join(command_dir, 'git_hooks')
        for prefix in prefixes:
            pattern = os.path.join(hooks_path, '%s-*.py' % prefix)
            for hook_filename in glob.glob(pattern):
                hook_name = os.path.splitext(
                    os.path.basename(hook_filename))[0]
                result[prefix][hook_name] = hook_filename
    return result


def _args():
    parser = ArgumentParser(
        description='A new command that runs in the project\'s "res" directory'
    )

    # Add arguments to the parser here
    group = parser.add_mutually_exclusive_group()
    hooks = _all_hooks()
    precommit_hooks = hooks['pre-commit'].keys()

    parser.add_argument('name', choices=precommit_hooks)

    group.add_argument('--on')
    group.add_argument('--off')

    args = Dodo.parse_args(parser,
                           config_args=[ConfigArg('/ROOT/src_dir', '--cwd')])

    args.git_hooks_dir = os.path.join(args.cwd, '.git', 'hooks')
    if not os.path.exists(args.git_hooks_dir):
        raise CommandError('Git hooks dir not found: %s' % args.git_hooks_dir)

    args.hooks = hooks
    return args


def lines_in_file(lines, filename):
    content = os.linesep.join(lines)

    if os.path.exists(filename):
        with open(filename) as ifs:
            if content in ifs.read():
                return

    with open(filename, 'a') as ofs:
        ofs.write(content + os.linesep)


def _get_hook(name, hooks):
    for p in prefixes:
        if name.startswith(p):
            hook_script_path = args.hooks[p][name]
            hook_script_name = os.path.basename(hook_script_path)
            return p, hook_script_path, hook_script_name
    return None


# Use safe=False if the script makes changes other than through Dodo.run
if Dodo.is_main(__name__, safe=False):
    args = _args()

    prefix, hook_script_path, hook_script_name = _get_hook(
        args.name, args.hooks)
    exists = os.path.exists(
        os.path.join(args.git_hooks_dir, os.path.basename(hook_script_path)))

    if exists and not args.on:
        Dodo.run(['rm', hook_script_name], cwd=args.git_hooks_dir)

    if not exists and not args.off:
        shell_script_path = os.path.join(args.git_hooks_dir, prefix)
        if not os.path.exists(shell_script_path):
            lines_in_file(['#!/bin/sh'], shell_script_path)
            Dodo.run(['chmod', '+x', shell_script_path])

        lines_in_file([
            'if [ -f .git/hooks/%s ]; then' % hook_script_name,
            '    python .git/hooks/%s' % hook_script_name,
            '    [ $? -eq 0 ] || exit $?;', 'fi'
        ], shell_script_path)

        Dodo.run(['cp', hook_script_path, args.git_hooks_dir])
