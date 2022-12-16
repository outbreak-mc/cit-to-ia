from pydantic import BaseModel


class ResourcepackModelDisplaySectionSchema(BaseModel):
    rotation: list[int | float] | None = None
    translation: list[int | float] | None = None
    scale: list[int | float] | None = None


class ResourcepackModelDisplaySchema(BaseModel):
    gui: ResourcepackModelDisplaySectionSchema | None = None
    ground: ResourcepackModelDisplaySectionSchema | None = None
    fixed: ResourcepackModelDisplaySectionSchema | None = None
    thirdperson_righthand: ResourcepackModelDisplaySectionSchema | None = None
    firstperson_righthand: ResourcepackModelDisplaySectionSchema | None = None
    head: ResourcepackModelDisplaySectionSchema | None = None


class ResourcepackModelSchema(BaseModel):
    parent: str | None
    textures: dict[str, str] | None = None
    elements: list[dict] | None = None
    display: ResourcepackModelDisplaySchema | None = None


class ItemsAdderInfoSchema(BaseModel):
    namespace: str


class ItemsAdderCategorySchema(BaseModel):
    enabled: bool
    icon: str
    name: str
    items: list[str] = []


class ItemsAdderResourceSchema(BaseModel):
    material: str
    generate: bool = False
    model_path: str


class ItemsAdderItemSchema(BaseModel):
    displayname: str
    lore: list[str] | None = None
    resource: ItemsAdderResourceSchema


class ItemsAdderConfigSchema(BaseModel):
    info: ItemsAdderInfoSchema
    items: dict[str, ItemsAdderItemSchema] = {}
    categories: dict[str, ItemsAdderCategorySchema] = {}


__all__ = [
    "ResourcepackModelSchema", "ResourcepackModelDisplaySectionSchema",
    "ItemsAdderInfoSchema", "ItemsAdderCategorySchema",
    "ItemsAdderCategorySchema", "ItemsAdderConfigSchema",
    "ItemsAdderResourceSchema", "ResourcepackModelDisplaySchema",
    "ItemsAdderItemSchema",

]
