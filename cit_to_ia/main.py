import json
from pathlib import Path

from anytree import RenderTree
from ruamel.yaml import YAML

from .schemas import *
from .utils import build_tree, models_iter

yaml = YAML()


class ModelsProcessor:
    def __init__(self, models_path: str | Path, logger=None):
        """ 
        - `models_path` - путь к папке `models` ресурспака

        - `logger` - объект любого логгера с методами `info()`, принимающим строку,
            и `exception()`, принимающим объект `Exception`.
        """
        self.models_path: Path = Path(models_path)
        self.logger = logger

    @property
    def namespace(self) -> str:
        return self.models_path.parent.name

    def _log_info(self, txt):
        if self.logger is not None:
            self.logger.info(txt)

    def _log_exception(self, txt):
        if self.logger is not None:
            self.logger.exception(txt)

    def fix_models_parents(self):
        """ 
        Исправляет относительные пути, начинающиеся с `./` в
        поле `parent` у моделей на правильные пути вида `namespace:item/model`
        """
        self._log_info("Processing model parents...")
        fixed = 0
        processed = 0

        for fullpath, namespace, relpath, modelname, ext in models_iter(self.models_path):
            model_path = fullpath / f"{modelname}.{ext}"
            namespaced_model_name = f"{namespace}:{relpath}/{modelname}"

            with open(model_path, "r", encoding="utf-8") as f:
                model = ResourcepackModelSchema(**json.load(f))

            if model.parent is not None and model.parent.startswith("./"):
                parent = model.parent[2:]
                rel_parent = f"{namespace}:{(Path(relpath).parent / parent).as_posix()}"
                model.parent = rel_parent

                with open(model_path, "w", encoding="utf-8") as f:
                    json.dump(model.dict(exclude_none=True), f)
                self._log_info(f"✅ {namespaced_model_name}")
                fixed += 1
            else:
                self._log_info(f"👁 {namespaced_model_name}")

            processed += 1

        self._log_info(f"{processed} models processed | {fixed} parent paths fixed")

    def create_itemsadder_configs(self, output_path: str | Path,
                                  lore: list[str] | None = None,
                                  ia_resource_material: str = "IRON_INGOT",
                                  category_name: str | None = None
                                  ) -> Path:
        """
        Создаёт файл конфига ItemsAdder, добавляя все модели как предметы, а
        также доблавяя категорию со всеми этими предметами

        - `output_path` - путь к файлу. Если указан путь к папке, 
            файл будет назван `items.yml`.

        - `lore` - описание, которое будет добавлено всем предметам

        - `ia_resource_material` - материал предметов

        - `category_name` - название категории. Если не указано, будет
            использовано пространство имён
        """
        ia_config = ItemsAdderConfigSchema(
            info=ItemsAdderInfoSchema(
                namespace=self.namespace
            ),
        )

        output_path = Path(output_path)
        if output_path.is_dir():
            output_path = output_path / "items.yml"

        self._log_info("Generating ItemsAdder config file...")

        for fullpath, namespace, relpath, filename, ext in models_iter(self.models_path):
            with open(fullpath / f"{filename}.{ext}", "r", encoding="utf-8") as f:
                model = ResourcepackModelSchema(**json.load(f))
                if model.textures is not None or model.elements is not None:
                    namespaced_filename = f"{namespace}:{filename}"

                    ia_config.items[filename] = ItemsAdderItemSchema(
                        displayname=filename,
                        lore=lore,
                        resource=ItemsAdderResourceSchema(
                            material=ia_resource_material,
                            generate=False,
                            model_path=f"{relpath}/{filename}"
                        )
                    )

                    category = ia_config.categories.get(namespace)
                    if category is None:
                        ia_config.categories[namespace] = ItemsAdderCategorySchema(
                            enabled=True,
                            icon=namespaced_filename,
                            name=category_name if category_name is not None else namespace
                        )

                    ia_config.categories[namespace].items.append(namespaced_filename)

        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(ia_config.dict(exclude_none=True), f)

        self._log_info(
            f"ItemsAdder config file with {len(ia_config.items)} "
            f"items saved as \"{str(output_path)}\""
        )

        return output_path

    def create_model_tree_txt(self, output_path: str | Path,
                              display_mark: str | None = None,
                              elements_mark: str | None = None) -> Path:
        """ 
        Создаёт текстовый файл с деревом зависимостей моделей.

        - `output_path` - путь к файлу. Если указан путь к папке, файл 
            будет назван `model_tree.txt`
        - `display_mark` - вставлять `display_mark` перед названием моделей, в 
            которых определено поле `display` 
        - `elements_mark` - вставлять `elements_mark` перед названием моделей, в 
            которых определено поле `elements` 

        Пример:
        ```
        namespace
        └── ⭐ namespace:block/parent_model
            └── 🌐 namespace:block/child_model_1
                └── namespace:block/child_model_2
        ```
        """
        output_path = Path(output_path)
        if output_path.is_dir():
            output_path = output_path / "model_tree.txt"

        self._log_info("Generating dependency tree file...")

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                tree = build_tree(self.models_path, display_mark, elements_mark)
                for pre, fill, node in RenderTree(tree):
                    f.write(f"{pre}{node.name}\n")
        except RuntimeError as e:
            self._log_exception(e)

        self._log_info(f"Dependency tree file saved as \"{str(output_path)}\"")

        return output_path


__all__ = ["ModelsProcessor"]
