import fire
from .main import ModelsProcessor
from loguru import logger
import sys
from pathlib import Path

logger.level("INFO", color="<green>")
logger.remove()
logger.add(
    sys.stdout,
    format="<level>{level: <8}</level> {message}",
    colorize=True
)


def run(
    models_path: str | Path,
    ia_configs_output_path: str | Path | None = None,
    tree_output_path: str | Path | None = None,
    display_mark: str = "⭐",
    elements_mark: str = "🌐",
    material: str = "IRON_INGOT",
    lore: str | None = None,
    category_name: str | None = None,
):
    models_path = Path(models_path)

    if ia_configs_output_path is None:
        ia_configs_output_path = models_path

    if tree_output_path is None:
        tree_output_path = models_path

    processor = ModelsProcessor(models_path, logger)
    processor.fix_models_parents()
    processor.create_itemsadder_configs(
        lore=lore.split("\\n") if lore is not None else None,
        category_name=category_name,
        ia_resource_material=material,
        output_path=ia_configs_output_path,
    )
    processor.create_model_tree_txt(
        output_path=tree_output_path,
        display_mark=display_mark,
        elements_mark=elements_mark,
    )


def main():
    fire.Fire(run)


if __name__ == "__main__":
    main()
