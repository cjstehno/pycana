from pathlib import Path

from click.testing import CliRunner

from pycana.commands.install import install
from pycana.services.database import db_info


def test_install(tmp_path):
    source_dir = str(Path(__file__).parent.parent.joinpath("resources"))
    data_dir = Path(tmp_path, 'data')
    data_dir.mkdir()
    db_file = str(Path(data_dir, 'test.db'))

    runner = CliRunner()
    result = runner.invoke(install, [
        '-d', str(source_dir),
        '-f', db_file,
        '--name-filter', '.xml',
    ])

    assert result.exit_code == 0

    assert db_info(db_file)["meta"]["total"] == 302

    assert result.output.splitlines()[0].startswith('Installing spells from ')
    assert result.output.splitlines()[4].endswith('Done.')
