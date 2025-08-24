from flask import Blueprint, request, jsonify, render_template
from service.models import Product, Category, db, DataValidationError
from service.common import status

bp = Blueprint("api", __name__)  


@bp.post("/products")
def create_product():
    try:
        prod = Product().deserialize(request.get_json() or {})
    except DataValidationError as e:
        return jsonify({"error": str(e)}), status.HTTP_400_BAD_REQUEST
    prod.create()
    return jsonify(prod.serialize()), status.HTTP_201_CREATED

@bp.get("/products/<int:pid>")
def read_product(pid: int):
    prod = Product.find(pid)
    if not prod:
        return (
            jsonify({"message": f"Product with id '{pid}' was not found."}),
            status.HTTP_404_NOT_FOUND,
        )
    return jsonify(prod.serialize()), status.HTTP_200_OK

@bp.put("/products/<int:pid>")
def update_product(pid: int):
    prod = Product.find(pid)
    if not prod:
        return (
            jsonify({"message": f"Product with id '{pid}' was not found."}),
            status.HTTP_404_NOT_FOUND,
        )
    try:
        prod.deserialize(request.get_json() or {})
    except DataValidationError as e:
        return jsonify({"error": str(e)}), status.HTTP_400_BAD_REQUEST
    prod.id = pid  
    prod.update()
    return jsonify(prod.serialize()), status.HTTP_200_OK

@bp.delete("/products/<int:pid>")
def delete_product(pid: int):
    prod = Product.find(pid)
    if prod:
        prod.delete()
    return "", status.HTTP_204_NO_CONTENT

@bp.get("/products")
def list_products():
    """List -> 200 + array; soporta filtros name/category/available"""
    q = Product.query
    name = request.args.get("name")
    cat = request.args.get("category")
    avail = request.args.get("available")

    if name:
        q = q.filter(Product.name == name)

    if cat:
        try:
            cat_value = getattr(Category, (cat or "").upper())
        except AttributeError:
            return (
                jsonify({"error": f"Invalid category '{cat}'"}),
                status.HTTP_400_BAD_REQUEST,
            )
        q = q.filter(Product.category == cat_value)

    if avail is not None:
        v = (avail or "").strip().lower()
        avail_value = v in ("true", "1", "yes", "y")
        q = q.filter(Product.available == avail_value)

    return jsonify([p.serialize() for p in q.all()]), status.HTTP_200_OK

@bp.delete("/admin/reset")
def admin_reset():
    db.session.query(Product).delete()
    db.session.commit()
    return "", status.HTTP_200_OK

@bp.get("/")
def index():
    return render_template("index.html")