import logging
from enum import Enum
from decimal import Decimal
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

# Configuración de logging
logger = logging.getLogger("flask.app")

# Instancia global de SQLAlchemy
db = SQLAlchemy()


class DataValidationError(Exception):
    """Error usado para datos inválidos al deserializar"""

    pass


class Category(Enum):
    """Enumeración de categorías válidas de productos"""

    UNKNOWN = 0
    CLOTHS = 1  
    FOOD = 2
    HOUSEWARES = 3
    AUTOMOTIVE = 4
    TOOLS = 5


class Product(db.Model):
    """Modelo Product que representa la tabla products"""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    available = db.Column(db.Boolean(), nullable=False, default=True)
    category = db.Column(
        db.Enum(Category),
        nullable=False,
        server_default=(Category.UNKNOWN.name),
    )

    def __repr__(self):
        return f"<Product {self.name} id=[{self.id}]>"

    def create(self):
        """Crea un nuevo producto en la base de datos"""
        logger.info("Creando %s", self.name)
        self.id = None
        db.session.add(self)
        db.session.commit()

    def update(self):
        """Actualiza un producto existente"""
        logger.info("Actualizando %s", self.name)
        if not self.id:
            raise DataValidationError("Update sin ID válido")
        db.session.commit()

    def delete(self):
        """Elimina un producto de la base de datos"""
        logger.info("Eliminando %s", self.name)
        db.session.delete(self)
        db.session.commit()

    def serialize(self) -> dict:
        """Convierte el objeto a diccionario (para API/JSON)"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": str(self.price),
            "available": self.available,
            "category": self.category.name,
        }

    def deserialize(self, data: dict):
        """Carga un objeto Product desde un diccionario"""
        try:
            self.name = data["name"]
            self.description = data["description"]
            self.price = Decimal(str(data["price"]))
            if isinstance(data["available"], bool):
                self.available = data["available"]
            else:
                raise DataValidationError("Invalid type for boolean [available]")
            self.category = getattr(Category, data["category"])
        except (KeyError, AttributeError, TypeError, ValueError) as error:
            raise DataValidationError("Invalid product: " + str(error)) from error
        return self

    @classmethod
    def init_db(cls, app: Flask):
        """Inicializa la base de datos con la app Flask"""
        logger.info("Inicializando base de datos")
        db.init_app(app)
        app.app_context().push()
        db.create_all()

    @classmethod
    def all(cls):
        """Devuelve todos los productos"""
        return cls.query.all()

    @classmethod
    def find(cls, product_id: int):
        """Busca un producto por ID"""
        return db.session.get(cls, product_id)

    @classmethod
    def find_by_name(cls, name: str):
        return cls.query.filter(cls.name == name).all()

    @classmethod
    def find_by_availability(cls, available: bool = True):
        return cls.query.filter(cls.available == available).all()

    @classmethod
    def find_by_category(cls, category: Category = Category.UNKNOWN):
        return cls.query.filter(cls.category == category).all()
