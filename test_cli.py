from click.testing import CliRunner
from pycana.commands.greet  import greet


def test_greet():
    runner = CliRunner()
    result = runner.invoke(greet, ['--name', 'Alice'])
    assert result.exit_code == 0
    assert result.output.strip() == 'Hello, Alice.'
