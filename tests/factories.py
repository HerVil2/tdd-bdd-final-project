import factory
from factory.fuzzy import FuzzyChoice, FuzzyDecimal

from service.models import Product, Category


class ProductFactory(factory.Factory):
    """Crea productos falsos para pruebas (unit/integration)"""

    class Meta:
        model = Product

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

    description = factory.Faker("text", max_nb_chars=120)

    price = FuzzyDecimal(0.5, 2000.0, 2)

    available = FuzzyChoice(choices=[True, False])

    category = FuzzyChoice(
        choices=[
            Category.UNKNOWN,
            Category.CLOTHS,  
            Category.FOOD,
            Category.HOUSEWARES,
            Category.AUTOMOTIVE,
            Category.TOOLS,
        ]
    )
