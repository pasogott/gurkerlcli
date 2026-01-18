"""Basic CLI tests."""

from click.testing import CliRunner

from gurkerlcli.cli import cli


def test_cli_version():
    """Test --version flag."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "gurkerlcli" in result.output


def test_cli_help():
    """Test --help flag."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "gurkerl.at" in result.output.lower() or "grocery" in result.output.lower()


def test_search_help():
    """Test search --help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["search", "--help"])
    assert result.exit_code == 0
    assert "search" in result.output.lower()


def test_cart_help():
    """Test cart --help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["cart", "--help"])
    assert result.exit_code == 0
    assert "cart" in result.output.lower()
