#!/usr/bin/env python

import os
import subprocess
import sys

FILE_EXTS = [".py"]


def call(args):
    return subprocess.check_output(args).decode('ascii', 'ignore')


def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


# check whether the given file matches any of the set extensions
def must_format_this_file(filename):
    return os.path.splitext(filename)[1] in FILE_EXTS


# necessary check for initial commit
output = call(["git", "rev-parse", "--verify", "HEAD"])
against = "HEAD" if output else "4b825dc642cb6eb9a060e54bf8d69288fbee4904"

yapf_exe = "yapf"
if which(yapf_exe) is None:
    print("Error: {yapf_exe} not found.\n".format(**locals()))
    sys.exit(1)

filenames = call([
    "git", "diff-index", "--cached", "--diff-filter=ACMR", "--name-only",
    against, "--"
]).split()

count_offending_files = 0
for filename in filenames:
    if not must_format_this_file(filename):
        continue

    # clang-format our sourcefile
    staged = call(["git", "show", ":" + filename])

    p1 = subprocess.Popen(["echo", staged], stdout=subprocess.PIPE)
    p2 = subprocess.Popen([yapf_exe],
                          stdin=p1.stdout,
                          stdout=subprocess.PIPE,
                          cwd=os.path.dirname(filename))
    formatted = p2.communicate()[0].decode('ascii', 'ignore')

    if not staged == formatted:
        if count_offending_files == 0:
            print("The following staged files are not yapf-formatted:\n")

        print(filename, "\n")
        count_offending_files += 1

if count_offending_files != 0:
    sys.exit(1)

sys.exit(0)
