# tests/factories.py
import factory
from factory.fuzzy import FuzzyChoice, FuzzyDecimal

from service.models import Product, Category


class ProductFactory(factory.Factory):
    """Crea productos falsos para pruebas (unit/integration)"""

    class Meta:
        model = Product

    # No seteamos 'id' para no interferir con la PK autoincremental
    name = FuzzyChoice(
        choices=[
            "Hat",
            "Pants",
            "Shirt",
            "Apple",
            "Banana",
            "Pots",
            "Towels",
            "Ford",
            "Chevy",
            "Hammer",
            "Wrench",
        ]
    )

    # Evita textos largos que excedan los 250 chars de la columna
    description = factory.Faker("text", max_nb_chars=120)

    # FuzzyDecimal ya devuelve Decimal; 2 decimales dentro del rango
    price = FuzzyDecimal(0.5, 2000.0, 2)

    available = FuzzyChoice(choices=[True, False])

    category = FuzzyChoice(
        choices=[
            Category.UNKNOWN,
            Category.CLOTHS,  # si tu Enum es CLOTHES, cámbialo aquí
            Category.FOOD,
            Category.HOUSEWARES,
            Category.AUTOMOTIVE,
            Category.TOOLS,
        ]
    )
