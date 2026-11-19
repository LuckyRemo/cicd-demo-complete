import io
import json

import pytest

from cicd_demo_complete.cli import main


def test_cli_prints_human_readable_summary(capsys):
    exit_code = main(["hello hello world", "--top", "2"])

    out = capsys.readouterr().out
    assert exit_code == 0
    assert "words:          3" in out
    assert "hello" in out
    assert "world" in out


def test_cli_prints_json(capsys):
    exit_code = main(["one two two", "--json"])

    out = capsys.readouterr().out
    payload = json.loads(out)
    assert exit_code == 0
    assert payload["words"] == 3
    assert payload["unique_words"] == 2
    assert payload["top"] == [["two", 2], ["one", 1]]


def test_cli_reads_stdin(capsys, monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO("alpha beta"))

    exit_code = main(["--json"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["words"] == 2


def test_cli_rejects_empty_input(capsys):
    exit_code = main(["   "])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "empty" in captured.err


def test_cli_rejects_bad_top(capsys):
    exit_code = main(["text", "--top", "0"])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "--top" in captured.err


@pytest.mark.parametrize("argv", [["--help"]])
def test_cli_help_exits_cleanly(argv):
    with pytest.raises(SystemExit) as exc:
        main(argv)
    assert exc.value.code == 0
