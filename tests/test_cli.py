import subprocess
import sys
from pathlib import Path

import pytest

import no_init


@pytest.mark.parametrize('args, expected', (
    (['folder1'], ([Path('folder1')], {'allow_empty': False})),
    (['folder1', 'folder2'], ([Path('folder1'), Path('folder2')], {'allow_empty': False})),
    (['--allow-empty', 'folder1'], ([Path('folder1')], {'allow_empty': True})),
    (['--allow-empty', 'folder1', 'folder2'], ([Path('folder1'), Path('folder2')], {'allow_empty': True})),
))
def test_parse_args(args, expected):
    assert no_init.parse_args(args) == expected


@pytest.mark.parametrize('args', ([], ['--allow-empty']))
def test_assert_at_least_1_path_passed(args):
    with pytest.raises(SystemExit):
        no_init.parse_args(args)


@pytest.mark.parametrize('paths, allow_empty, code, stdout', [
    ((Path('test_data/module_0'),), False, 0, ''),
    ((Path('test_data/module_0'), Path('test_data/module_1')), False, 0, ''),
    ((Path('test_data/module_2'),), False, 1, 'test_data/module_2/__init__.py\nerror: found 1 __init__.py files\n'),
    ((Path('test_data/module_2'),), True, 0, ''),
    ((Path('test_data/module_0'), Path('test_data/module_2'),), True, 0, ''),
    ((Path('test_data/module_3'),), True, 1, 'test_data/module_3/__init__.py\nerror: found 1 non_empty__init__.py files\n'),
    ((Path('test_data/module_3'), Path('test_data/module_0'),), True, 1, 'test_data/module_3/__init__.py\nerror: found 1 non_empty__init__.py files\n'),
    ((Path('test_data/module_2'), Path('test_data/module_3'),), False, 1, 'test_data/module_2/__init__.py\ntest_data/module_3/__init__.py\nerror: found 2 __init__.py files\n'),
])
def test_check(paths, allow_empty, code, stdout, capsys):
    assert no_init.check(*paths, allow_empty=allow_empty) == code
    out, err = capsys.readouterr()
    assert out == stdout

    args = [str(p) for p in paths]
    if allow_empty:
        args = ['--allow-empty'] + args
    p = subprocess.run((sys.executable, '-m', 'no_init', *args), text=True, capture_output=True)
    assert p.returncode == code
    assert p.stdout == stdout
