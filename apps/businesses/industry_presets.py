"""Starter categories offered during onboarding, by industry."""

from .models import Industry

CATEGORY_PRESETS: dict[str, list[str]] = {
    Industry.CLOTHING: [
        "Remeras",
        "Pantalones",
        "Buzos y camperas",
        "Vestidos y polleras",
        "Ropa interior",
        "Calzado",
        "Accesorios",
    ],
    Industry.FOOD: [
        "Panificados",
        "Dulces y postres",
        "Comidas elaboradas",
        "Bebidas",
        "Almacén",
        "Sin TACC",
    ],
    Industry.BEAUTY: [
        "Cuidado facial",
        "Cuidado corporal",
        "Cabello",
        "Maquillaje",
        "Perfumes",
        "Uñas",
    ],
    Industry.HOME: [
        "Velas y aromas",
        "Textiles",
        "Cocina y mesa",
        "Decoración",
        "Iluminación",
        "Organización",
    ],
    Industry.ELECTRONICS: [
        "Celulares",
        "Accesorios para celular",
        "Audio",
        "Computación",
        "Cables y cargadores",
        "Gaming",
    ],
    Industry.CRAFTS: [
        "Bijouterie",
        "Cerámica",
        "Tejidos",
        "Papelería",
        "Regalos personalizados",
        "Materiales",
    ],
    Industry.OTHER: [],
}


def presets_for(industry: str) -> list[str]:
    return list(CATEGORY_PRESETS.get(industry, []))
