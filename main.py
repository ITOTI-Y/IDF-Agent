import time
from pathlib import Path
from typing import Annotated, Optional

import typer

from src.converter_manager import ConverterManager
from src.runner.runner import EnergyPlusRunner
from src.utils.logging import get_logger, setup_logger

app = typer.Typer(
    name="idf-agent",
    help="IDF Agent - EnergyPlus IDF 文件转换和运行工具",
    add_completion=False,
)

logger_time = time.strftime("%Y%m%d_%H%M%S")
setup_logger(
    level="INFO",
    console_output=True,
    log_file_path=Path(f"./logs/{logger_time}.log"),
)
logger = get_logger(__name__)


@app.command()
def main(
    yaml_file: Annotated[
        Path,
        typer.Argument(
            help="YAML File Path",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
        ),
    ] = Path("./schemas/building_schema.yaml"),
    epw_file: Annotated[
        Path,
        typer.Argument(
            help="EPW Weather File Path",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
        ),
    ] = Path("./dependencies/Shenzhen.epw"),
    output_directory: Annotated[
        Optional[Path],
        typer.Option(
            "--output-dir",
            "-o",
            help="Output Directory Path",
            file_okay=False,
            dir_okay=True,
            resolve_path=True,
        ),
    ] = None,
) -> None:
    idd_file = Path("./dependencies/Energy+.idd")
    idf_file_output = Path(f"./output/idf/output_{logger_time}.idf")

    manager = ConverterManager(idd_file, yaml_file)
    manager.convert_all()
    manager.save_idf(idf_file_output)

    ep_runner = EnergyPlusRunner(manager._idf)
    ep_runner.run_idf(epw_file_path=epw_file)


if __name__ == "__main__":
    app()
