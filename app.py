from flask import Flask,request
from db import db,ItemModel,StoreModel
import uuid
from flask_smorest import abort
import os



app = Flask(__name__)

# port = int(os.environ.get("PORT", 5000))
# app.run(host="0.0.0.0", port=port)


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False



db.init_app(app)


with app.app_context():
    db.create_all()


@app.get("/")
def home():
    return {"message": "API is running"}

@app.post("/store")
def addStoreDetail():

    store_data = request.get_json()
     
    if "name" not in store_data:
        abort(400, message="Bad request. Payload does not contain the name")
    
    if StoreModel.query.filter_by(name=store_data["name"]).first():
        return {"message": "Store Name already exists"}

    store = StoreModel(
        id=uuid.uuid4().hex,
        name=store_data["name"])
    
    db.session.add(store)
    db.session.commit()

    return {"id": store.id, "name": store.name}, 201

@app.get("/store")
def get_stores():
    stores = StoreModel.query.all()
    return {
        "stores" : [
            { "id" : store.id , "name" : store.name}
            for store in stores
        ]
    }

@app.get("/store/<string:store_id>")
def get_store(store_id):
    store = StoreModel.query.get(store_id)

    if not store:
        return {"message" : "Store not exists"}
    
    return {
        "id" : store.id,
        "name" : store.name,
        "items" : [
            {"id" : item.id, "name" : item.name, "price" : item.price}
            for item in store.items
        ]
    }

@app.delete("/store/<string:store_id>")
def delete_store(store_id):
    store = StoreModel.query.get(store_id)

    if not store:
        abort(404, message="Store not found")

    db.session.delete(store)
    db.session.commit()

    return {"message": "Store deleted"}




@app.post("/item")
def create_item():
    data = request.get_json()
    requirement_fields = {"name","price","store_id"}

    if not requirement_fields.issubset(data):
        abort(400, message="name, price and store_id are required")

    store = StoreModel.query.get(data["store_id"])

    if not store:
        abort(404, message="Store not found")

    item = ItemModel(
        id=uuid.uuid4().hex,
        name=data["name"],
        price=data["price"],
        store_id=data["store_id"]
    )

    db.session.add(item)
    db.session.commit()

    return {
        "id" : item.id,
        "name": item.name,
        "price": item.price,
        "store_id": item.store_id
    }, 201

@app.get("/item")
def get_items():
    items = ItemModel.query.all()
    return {
        "items": [
            {
                "id": item.id,
                "name": item.name,
                "price": item.price,
                "store_id": item.store_id
            }
            for item in items
        ]
    }


@app.get("/item/<string:item_id>")
def get_item(item_id):
    item = ItemModel.query.get(item_id)

    if not item:
        abort(404, message="Item not found")

    return {
        "id": item.id,
        "name": item.name,
        "price": item.price,
        "store_id": item.store_id
    }


@app.put("/item/<string:item_id>")
def update_item(item_id):
    item = ItemModel.query.get(item_id)

    if not item:
        abort(404, message="Item not found")

    data = request.get_json()

    if "name" in data:
        item.name = data["name"]
    if "price" in data:
        item.price = data["price"]

    db.session.commit()

    return {
        "id": item.id,
        "name": item.name,
        "price": item.price,
        "store_id": item.store_id
    }


@app.delete("/item/<string:item_id>")
def delete_item(item_id):
    item = ItemModel.query.get(item_id)

    if not item:
        abort(404, message="Item not found")

    db.session.delete(item)
    db.session.commit()

    return {"message": "Item deleted"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)






