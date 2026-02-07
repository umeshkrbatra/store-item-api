from flask import Flask,request
from db import db,ItemModel,StoreModel
import uuid
from flask_smorest import abort
import os


app = Flask(__name__)
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)



app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


with app.app_context():
    db.create_all()


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


# @app.post("/store")
# def addStoreDetail():

#     store_data = request.get_json()
     
#     if "name" not in store_data:
#         abort(400, message="Bad request. Payload does not contain the name")
    

#     for store in stores.values():
#         if store_data["name"] == store["name"]:
#             return {"message": "Store Name already exists"}
        
    
#     store_id = uuid.uuid4().hex
#     store = {**store_data, "id":store_id}
#     stores[store_id] = store
    
#     return {"message":"values stored"}



# @app.get("/store")
# def getStoreList():
#     return {"stores": list(stores.values())}


# @app.get("/store/<store_id>")
# def getStoreId(store_id):
#     try:
#         return stores[store_id]
#     except KeyError:
#         return {"message" : "Mentioned Store Id does not exists"}


# @app.delete("/store/<store_id>")
# def deleteStoreId(store_id):
#     try:
#         del stores[store_id]
#     except KeyError:
#         return   {"message" : "Mentioned Store Id deleted"}
    

    

     

# @app.post("/item")
# def createItems():
#     item_data = request.get_json()

#     if ("name" not in item_data 
#         or "price" not in item_data 
#         or "store_id" not in item_data) :
#         abort(400, message="Bad Request. Payload does not contains name or price or store_id")


#     if item_data["store_id"] not in stores:
#         return {"message" : "store id does not exist"}


#     item_id = uuid.uuid4().hex
#     item = {**item_data, "id":item_id}
#     items[item_id] = item

#     return {"message": "Item Saved"}


# @app.get("/item")
# def getitemlist():
#     return {"items" : list(items.values())}
    

# @app.get("/item/<string:item_id>")
# def getspecificitem(item_id):
#     try:
#         return items[item_id]
#     except KeyError:
#         return {"message": "item does not exists"}



# @app.delete("/item/<string:item_id>")
# def deletespecificitem(item_id):
#     try:
#         del stores[item_id]
#         return {"message" : "Mentioned Item deleted"}
#     except KeyError:
#         return   {"message" : "Mentioned Item Id does not exist"}
    

# @app.put("/item/<string:item_id>")
# def updatespecificitem(item_id):
#     item_data = request.get_json()

#     if ("name" not in item_data 
#         or "price" not in item_data ) :
#         abort(400, message="Bad Request. Payload does not contains name or price")

#     if (item_id not in items):
#         return {"message" : "id does not exists"}

#     item = items[item_id]
#     item |= item_data

#     return {"message": "Item value is updated"}

        
#     store_id = uuid.uuid4().hex
#     print(store_id)
#     store = {**store_data, "id":store_id}
#     stores[store_id] = store


    
#     return 200, store
    
    










# @app.get("/store")
# def get_stores():
#     return {"stores" : list(stores.values())}



# @app.post("/store")
# def create_store():
#     store_data = request.get_json()

#     if "name" not in store_data:
#         abort(
#             400,
#             message="Bad Request. Ensure Name must be included in the JSON payload"
#         )

#     for store in stores.values():
#         if store_data["name"] == store["name"]:
#             return {"message" : "store already exists"}

#     store_id = uuid.uuid4().hex
#     store = {**store_data, "id": store_id} 
#     stores[store_id] = store
#     return store, 201


# @app.get("/store/<string:store_id>")
# def get_store(store_id):
#     try:
#         return stores[store_id]
#     except KeyError:
#         abort(404, message="store not found" )


# @app.delete("/store/<string:store_id>")
# def delete_store(store_id):
#     try:
#         del stores[store_id]
#         return {"message" : "Store Id is deleted"}
#     except KeyError:
#         abort(404, message="store not found" )
    



# @app.post("/item")
# def create_item():
#     item_data = request.get_json()
#     if ("price" not in item_data 
#         or "store_id" not in item_data
#         or "name" not in item_data):
#         abort(
#             400,
#             message="Bad Request. Ensure price, name and store_id must be in a payload"
#         )
#     if item_data["store_id"] not in stores:
#         # abort(404, message="store not found" )
#         return {"message" : "store not found"}
    
#     item_id = uuid.uuid4().hex
#     item = {**item_data, "id": item_id}
#     items[item_id] = item

#     return item, 200

# @app.get("/item")
# def get_all_tems():
#     return {"items" : list(items.values())}


# @app.get("/item/<string:item_id>")
# def get_item(item_id):
#     try:
#         return items[item_id]
#     except KeyError:
#         abort(404, message="item not found" )


# @app.delete("/item/<string:item_id>")
# def delete_item(item_id):
#     try:
#         del items[item_id]
#         return {"message" : "Item deleted"}
#     except KeyError:
#         abort(404, message="item not found" )


# @app.put("/item/<string:item_id>")
# def put_item(item_id):

#     item_data = request.get_json()

#     if "price" not in item_data or "name" not in item_data:
#         abort(400, message="Bad request")
#     try:
#         item = items[item_id]
#         item |= item_data
#         return item
#     except KeyError:
#         abort(404, message="item not found" )






################################################################################


# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000)















# app.config["API_TITLE"] = "Store & Item API"
# app.config["API_VERSION"] = "v1"
# app.config["OPENAPI_VERSION"] = "3.0.3"
# app.config["OPENAPI_URL_PREFIX"] = "/"
# app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
# app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False








# store = [
#     {
#         "name" : "spencer",
#         "items" : [
#             {
#                 "name" : "snacks",
#                 "price" : "20"
#             }
#         ]
#     }
    
# ]




# @app.route("/")
# def hello_world():
#     return "Hello World"


# @app.get("/store")
# def get_store():
#     return store


# @app.post("/store")
# def add_store():
#     request_data = request.get_json()
#     new_data = {"name": request_data["name"], "items": []}
#     store.append(new_data)
#     return store, 200

# @app.post("/store/<string:name>/item")
# def add_items(name):
#     request_data = request.get_json()
#     for stor in store:
#         if stor["name"] == name:
#             new_data = {"name": request_data["name"], "price": request_data["price"]}
#             stor["items"].append(new_data)
#             return stor["name"], 200
#     return { "message" : "store not found"}


# @app.get("/store/<string:name>")
# def get_store_details(name):
#     for stor in store:
#         if stor["name"] == name:
#             return stor
#     return {"message": "Store Not Found"}, 404


# @app.get("/store/<string:name>/item")
# def get_items_in_store(name):
#     for stor in store:
#         if stor["name"] == name:
#             return {"items": stor["items"]}
#     return {"message": "Store Not Found"}, 404





































# app = Flask(__name__)

# if __name__ == "__main__":
#     app.run()


# app.run(host="0.0.0.0", port=5005)


