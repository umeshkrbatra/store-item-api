from flask import Flask,request
from db import db,ItemModel,StoreModel
import uuid
from flask_smorest import abort
import os
from flask.views import MethodView
# Swagger imports
from flask_smorest import Api, Blueprint, abort
from marshmallow import Schema, fields


app = Flask(__name__)

# ==============================
# Swagger Configuration
# ==============================

app.config["API_TITLE"] = "Store & Item API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"

# Swagger UI URL
app.config["OPENAPI_URL_PREFIX"] = "/api"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/docs"
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
# port = int(os.environ.get("PORT", 5000))
# app.run(host="0.0.0.0", port=port)


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False



db.init_app(app)

api = Api(app)

with app.app_context():
    db.create_all()



# Schemas
class StoreSchema(Schema):
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)


class ItemSchema(Schema):
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    price = fields.Float(required=True)
    store_id = fields.Str(required=True)

# Blueprints
store_blp = Blueprint("Stores", "stores", description="Store operations")
item_blp = Blueprint("Items", "items", description="Item operations")


@store_blp.route("/")
class Home(MethodView):
    def get(self):
        """API Health Check"""
        return {"message": "API is running"}

@store_blp.route("/store")
class StoreList(MethodView):

    @store_blp.response(200, StoreSchema(many=True))
    def get(self):
        """Get all stores"""
        stores = StoreModel.query.all()
        return stores

    @store_blp.arguments(StoreSchema)
    @store_blp.response(201, StoreSchema)
    def post(self, store_data):
        """Create a new store"""

        if StoreModel.query.filter_by(name=store_data["name"]).first():
            abort(400, message="Store already exists")

        store = StoreModel(
            id=uuid.uuid4().hex,
            name=store_data["name"]
        )

        db.session.add(store)
        db.session.commit()

        return store


@store_blp.route("/store/<string:store_id>")
class StoreResource(MethodView):

    @store_blp.response(200, StoreSchema)
    def get(self, store_id):
        """Get store by ID"""
        store = StoreModel.query.get(store_id)

        if not store:
            abort(404, message="Store not found")

        return store

    def delete(self, store_id):
        """Delete store"""
        store = StoreModel.query.get(store_id)

        if not store:
            abort(404, message="Store not found")

        db.session.delete(store)
        db.session.commit()

        return {"message": "Store deleted"}

# Item APIs

@item_blp.route("/item")
class ItemList(MethodView):

    @item_blp.response(200, ItemSchema(many=True))
    def get(self):
        """Get all items"""
        items = ItemModel.query.all()
        return items

    @item_blp.arguments(ItemSchema)
    @item_blp.response(201, ItemSchema)
    def post(self, item_data):
        """Create item"""

        store = StoreModel.query.get(item_data["store_id"])

        if not store:
            abort(404, message="Store not found")

        item = ItemModel(
            id=uuid.uuid4().hex,
            name=item_data["name"],
            price=item_data["price"],
            store_id=item_data["store_id"]
        )

        db.session.add(item)
        db.session.commit()

        return item


@item_blp.route("/item/<string:item_id>")
class ItemResource(MethodView):

    @item_blp.response(200, ItemSchema)
    def get(self, item_id):
        """Get item by ID"""

        item = ItemModel.query.get(item_id)

        if not item:
            abort(404, message="Item not found")

        return item

    @item_blp.arguments(ItemSchema(partial=True))
    @item_blp.response(200, ItemSchema)
    def put(self, update_data, item_id):
        """Update item"""

        item = ItemModel.query.get(item_id)

        if not item:
            abort(404, message="Item not found")

        if "name" in update_data:
            item.name = update_data["name"]

        if "price" in update_data:
            item.price = update_data["price"]

        db.session.commit()

        return item

    def delete(self, item_id):
        """Delete item"""

        item = ItemModel.query.get(item_id)

        if not item:
            abort(404, message="Item not found")

        db.session.delete(item)
        db.session.commit()

        return {"message": "Item deleted"}


# Register Blueprints
api.register_blueprint(store_blp)
api.register_blueprint(item_blp)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# @app.get("/")
# def home():
#     return {"message": "API is running"}

# @app.post("/store")
# def addStoreDetail():

#     store_data = request.get_json()
     
#     if "name" not in store_data:
#         abort(400, message="Bad request. Payload does not contain the name")
    
#     if StoreModel.query.filter_by(name=store_data["name"]).first():
#         return {"message": "Store Name already exists"}

#     store = StoreModel(
#         id=uuid.uuid4().hex,
#         name=store_data["name"])
    
#     db.session.add(store)
#     db.session.commit()

#     return {"id": store.id, "name": store.name}, 201

# @app.get("/store")
# def get_stores():
#     stores = StoreModel.query.all()
#     return {
#         "stores" : [
#             { "id" : store.id , "name" : store.name}
#             for store in stores
#         ]
#     }

# @app.get("/store/<string:store_id>")
# def get_store(store_id):
#     store = StoreModel.query.get(store_id)

#     if not store:
#         return {"message" : "Store not exists"}
    
#     return {
#         "id" : store.id,
#         "name" : store.name,
#         "items" : [
#             {"id" : item.id, "name" : item.name, "price" : item.price}
#             for item in store.items
#         ]
#     }

# @app.delete("/store/<string:store_id>")
# def delete_store(store_id):
#     store = StoreModel.query.get(store_id)

#     if not store:
#         abort(404, message="Store not found")

#     db.session.delete(store)
#     db.session.commit()

#     return {"message": "Store deleted"}




# @app.post("/item")
# def create_item():
#     data = request.get_json()
#     requirement_fields = {"name","price","store_id"}

#     if not requirement_fields.issubset(data):
#         abort(400, message="name, price and store_id are required")

#     store = StoreModel.query.get(data["store_id"])

#     if not store:
#         abort(404, message="Store not found")

#     item = ItemModel(
#         id=uuid.uuid4().hex,
#         name=data["name"],
#         price=data["price"],
#         store_id=data["store_id"]
#     )

#     db.session.add(item)
#     db.session.commit()

#     return {
#         "id" : item.id,
#         "name": item.name,
#         "price": item.price,
#         "store_id": item.store_id
#     }, 201

# @app.get("/item")
# def get_items():
#     items = ItemModel.query.all()
#     return {
#         "items": [
#             {
#                 "id": item.id,
#                 "name": item.name,
#                 "price": item.price,
#                 "store_id": item.store_id
#             }
#             for item in items
#         ]
#     }


# @app.get("/item/<string:item_id>")
# def get_item(item_id):
#     item = ItemModel.query.get(item_id)

#     if not item:
#         abort(404, message="Item not found")

#     return {
#         "id": item.id,
#         "name": item.name,
#         "price": item.price,
#         "store_id": item.store_id
#     }


# @app.put("/item/<string:item_id>")
# def update_item(item_id):
#     item = ItemModel.query.get(item_id)

#     if not item:
#         abort(404, message="Item not found")

#     data = request.get_json()

#     if "name" in data:
#         item.name = data["name"]
#     if "price" in data:
#         item.price = data["price"]

#     db.session.commit()

#     return {
#         "id": item.id,
#         "name": item.name,
#         "price": item.price,
#         "store_id": item.store_id
#     }


# @app.delete("/item/<string:item_id>")
# def delete_item(item_id):
#     item = ItemModel.query.get(item_id)

#     if not item:
#         abort(404, message="Item not found")

#     db.session.delete(item)
#     db.session.commit()

#     return {"message": "Item deleted"}


