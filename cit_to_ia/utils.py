import json
import os
from pathlib import Path

from anytree import Node

from .schemas import *


def models_iter(path: str | Path):
    """ 
    Итератор по всем моделям (файлам `.json`) в ресурспаке. Возвращает
    кортеж из 4 элементов: 

    - Объект `Path` пути к папке, в которой находится файл
    - Пространство имён ресурспака (название папки перед models)
    - Путь к папке модели относительно `/models/` (т.е. только то, что после `/models/`)
    - Имя файла без расширения
    - Расширение файла (на текущий момент существуют только модели в формате `.json`)
    """
    for p, dirs, files in os.walk(path, False):
        for file in files:
            if file.endswith(".json"):
                fullpath = Path(p)
                first_part, relpath = fullpath.as_posix().split("/models/")
                _, namespace = first_part.rsplit("/", 1)
                modelname, ext = file.rsplit(".", 1)
                yield (fullpath, namespace, relpath, modelname, ext)


def build_tree(models_path: str | Path,
               mark_models_with_display: str | None = None,
               mark_models_with_elements: str | None = None
               ) -> Node:
    """
    Строит дерево зависимостей моделей по их `parent`.

    - `models_path` - путь к папке `models` ресурспака

    - `mark_models_with_display` - помечать символом `mark_models_with_display` 
        названия моделей, в которых определено поле display

    - `mark_models_with_elements` - помечать символом `mark_models_with_elements` 
        названия моделей, в которых определены элементы
    """
    path = Path(models_path)
    namespace = str(path.parent.name)

    root_node = Node(namespace)
    node_map = {}

    tree_build_q = [(fullpath, namespace, relpath, filename, ext)
                    for fullpath, namespace, relpath, filename, ext in models_iter(models_path)]

    def iter_q():
        while len(tree_build_q) > 0:
            yield tree_build_q.pop()

    steps_not_changed = 0

    for fullpath, namespace, relpath, filename, ext in iter_q():
        with open(fullpath / f"{filename}.{ext}", "r", encoding="utf-8") as f:
            model = ResourcepackModelSchema(**json.load(f))

            nodename = f"{namespace}:{relpath}/{filename}"
            nodedisplayname = nodename

            if mark_models_with_display and model.display is not None:
                nodedisplayname = mark_models_with_display + " " + nodedisplayname
            if mark_models_with_elements and model.elements is not None:
                nodedisplayname = mark_models_with_elements + " " + nodedisplayname

            if model.parent is None:
                node_map[nodename] = Node(nodedisplayname, parent=root_node)
            else:
                parent_node = node_map.get(model.parent)
                if parent_node is None:
                    tree_build_q.insert(0, (fullpath, namespace, relpath, filename, ext))
                    steps_not_changed += 1
                else:
                    node_map[nodename] = Node(nodedisplayname, parent=parent_node)
                    steps_not_changed = 0

        if steps_not_changed > len(tree_build_q):
            raise RuntimeError(
                "Не удалось построить дерево зависимостей. Такое может произойти, "
                "если у какой-то из моделей указан несуществующий родитель.",
                steps_not_changed, len(tree_build_q)
            )

    return root_node


__all__ = ["models_iter", "build_tree"]
