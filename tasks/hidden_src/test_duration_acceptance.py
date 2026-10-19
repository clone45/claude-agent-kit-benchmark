"""Hidden acceptance tests for the Duration parameter type task (harness-authored)."""

import datetime

import pytest

import click


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("90s", datetime.timedelta(seconds=90)),
        ("5m", datetime.timedelta(minutes=5)),
        ("1h30m", datetime.timedelta(hours=1, minutes=30)),
        ("1h 30m", datetime.timedelta(hours=1, minutes=30)),
        ("2d", datetime.timedelta(days=2)),
        ("1D2H3M4S", datetime.timedelta(days=1, hours=2, minutes=3, seconds=4)),
        ("45", datetime.timedelta(seconds=45)),
        ("0s", datetime.timedelta(0)),
        ("0", datetime.timedelta(0)),
        ("  10s ", datetime.timedelta(seconds=10)),
    ],
)
def test_duration_convert(value, expected):
    assert click.Duration().convert(value, None, None) == expected


def test_duration_timedelta_passthrough():
    td = datetime.timedelta(minutes=3)
    assert click.Duration().convert(td, None, None) is td


def test_duration_int_is_seconds():
    assert click.Duration().convert(45, None, None) == datetime.timedelta(seconds=45)


@pytest.mark.parametrize(
    "value", ["", "5x", "1.5h", "-5s", "30m1h", "1h1h", "h", "abc"]
)
def test_duration_invalid(value):
    with pytest.raises(click.BadParameter) as exc_info:
        click.Duration().convert(value, None, None)
    message = str(exc_info.value)
    assert value in message or repr(value) in message


def test_duration_rejects_other_types():
    with pytest.raises(click.BadParameter):
        click.Duration().convert(["1h"], None, None)


def test_duration_metadata():
    duration = click.Duration()
    assert duration.name == "duration"
    assert repr(duration) == "DURATION"
    info = duration.to_info_dict()
    assert info["param_type"] == "Duration"
    assert info["name"] == "duration"


def test_duration_in_command(runner):
    @click.command()
    @click.option("--timeout", type=click.Duration())
    def cli(timeout):
        click.echo(str(int(timeout.total_seconds())))

    result = runner.invoke(cli, ["--timeout", "1h30m"])
    assert result.exit_code == 0, result.output
    assert result.output == "5400\n"

    bad = runner.invoke(cli, ["--timeout", "5x"])
    assert bad.exit_code == 2
    assert "5x" in bad.output


def test_duration_help_metavar(runner):
    @click.command()
    @click.option("--timeout", type=click.Duration(), help="How long to wait.")
    def cli(timeout):
        pass

    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "--timeout DURATION" in result.output
