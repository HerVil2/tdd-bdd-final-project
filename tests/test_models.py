import unittest
from decimal import Decimal

from service.app import create_app
from service.models import Product, DataValidationError, db
from tests.factories import ProductFactory


def _as_list(found):
    """Devuelve siempre una lista (convierte Query -> list si hiciera falta)"""
    return found if isinstance(found, list) else list(found.all())


def _size(found):
    """Tamaño robusto para list o Query"""
    return len(_as_list(found))


class TestProductModel(unittest.TestCase):
    """Pruebas del modelo Product"""

    @classmethod
    def setUpClass(cls):
        # App en modo testing con SQLite en memoria
        cls.app = create_app(testing=True)
        cls.ctx = cls.app.app_context()
        cls.ctx.push()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        cls.ctx.pop()

    def setUp(self):
        # Limpia tabla antes de cada test
        db.session.query(Product).delete()
        db.session.commit()

    # ---------- READ ----------
    def test_read_a_product(self):
        """It should Read a Product"""
        product = ProductFactory()
        product.create()
        self.assertIsNotNone(product.id)

        found = Product.find(product.id)
        self.assertIsNotNone(found)
        self.assertEqual(found.id, product.id)
        self.assertEqual(found.name, product.name)
        self.assertEqual(found.description, product.description)
        self.assertEqual(Decimal(str(found.price)), Decimal(str(product.price)))
        self.assertEqual(found.available, product.available)
        self.assertEqual(found.category, product.category)

    # ---------- UPDATE ----------
    def test_update_a_product(self):
        """It should Update a Product"""
        product = ProductFactory(description="orig")
        product.create()
        pid = product.id

        product.description = "updated"
        product.price = Decimal("123.45")
        product.update()

        self.assertEqual(len(Product.all()), 1)

        reloaded = Product.find(pid)
        self.assertEqual(reloaded.id, pid)
        self.assertEqual(reloaded.description, "updated")
        self.assertEqual(Decimal(str(reloaded.price)), Decimal("123.45"))

    # ---------- DELETE ----------
    def test_delete_a_product(self):
        """It should Delete a Product"""
        product = ProductFactory()
        product.create()
        self.assertEqual(len(Product.all()), 1)

        product.delete()
        self.assertEqual(len(Product.all()), 0)

    # ---------- LIST ALL ----------
    def test_list_all_products(self):
        """It should List all Products in the database"""
        products = Product.all()
        self.assertEqual(products, [])

        for _ in range(5):
            p = ProductFactory()
            p.create()

        products = Product.all()
        self.assertEqual(len(products), 5)

    # ---------- FIND BY NAME ----------
    def test_find_by_name(self):
        """It should Find Products by Name"""
        products = ProductFactory.create_batch(5)
        for p in products:
            p.create()

        name = products[0].name
        expected = len([p for p in products if p.name == name])

        found = Product.find_by_name(name)
        self.assertEqual(_size(found), expected)
        for p in _as_list(found):
            self.assertEqual(p.name, name)

    # ---------- FIND BY CATEGORY ----------
    def test_find_by_category(self):
        """It should Find Products by Category"""
        products = ProductFactory.create_batch(10)
        for p in products:
            p.create()

        category = products[0].category
        expected = len([p for p in products if p.category == category])

        found = Product.find_by_category(category)
        self.assertEqual(_size(found), expected)
        for p in _as_list(found):
            self.assertEqual(p.category, category)

    # ---------- FIND BY AVAILABILITY ----------
    def test_find_by_availability(self):
        """It should Find Products by Availability"""
        products = ProductFactory.create_batch(10)
        for p in products:
            p.create()

        available_flag = products[0].available
        expected = len([p for p in products if p.available == available_flag])

        found = Product.find_by_availability(available_flag)
        self.assertEqual(_size(found), expected)
        for p in _as_list(found):
            self.assertEqual(p.available, available_flag)

    # ---------- EXTRA: deserialize errors (para cobertura alta) ----------
    def test_deserialize_errors(self):
        """It should raise DataValidationError on bad payloads"""
        p = Product()
        # Falta 'name'
        with self.assertRaises(DataValidationError):
            p.deserialize(
                {
                    "description": "x",
                    "price": "1.00",
                    "available": True,
                    "category": "FOOD",
                }
            )
        # available mal tipeado
        with self.assertRaises(DataValidationError):
            p.deserialize(
                {
                    "name": "X",
                    "description": "x",
                    "price": "1.00",
                    "available": "yes",
                    "category": "FOOD",
                }
            )
        # category inválida
        with self.assertRaises(DataValidationError):
            p.deserialize(
                {
                    "name": "X",
                    "description": "x",
                    "price": "1.00",
                    "available": True,
                    "category": "NOPE",
                }
            )

    def test_update_without_id_raises(self):
        """It should raise when updating without ID"""
        from service.models import Product, DataValidationError

        p = Product()  # id None
        with self.assertRaises(DataValidationError):
            p.update()

    def test_repr_and_serialize(self):
        """It should return a nice repr and serialize fields"""
        p = ProductFactory()
        p.create()
        s = p.serialize()
        assert s["category"] == p.category.name
        assert "Product" in repr(p)
