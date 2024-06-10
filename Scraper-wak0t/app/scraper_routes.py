from flask import Blueprint, render_template, request, redirect, url_for
from pymongo import MongoClient, UpdateOne
from .scraper import EbayScraper
from .forms import ScraperForm, FilterForm

scraper_bp = Blueprint('scraper', __name__)

# Połączenie z bazą danych MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["scraper_db"]


@scraper_bp.route('/', methods=['GET', 'POST'])
def index():
    form = ScraperForm()
    items = []
    collections = db.list_collection_names()

    if request.method == 'POST' and form.validate():
        query = form.query.data
        min_price = form.min_price.data or 0
        max_price = form.max_price.data or 999999
        sort_order = form.sort_order.data
        free_shipping = form.free_shipping.data
        exclude_price_range = form.exclude_price_range.data

        scraper = EbayScraper()
        items = scraper.scrape(query, min_price, max_price, sort_order, free_shipping, exclude_price_range)

        # Przygotowanie operacji bulk_write
        operations = []
        for item in items:
            operations.append(
                UpdateOne({"_id": item["_id"]}, {"$set": item}, upsert=True)
            )

        # Wykonanie operacji bulk_write
        collection = db[query]
        if operations:
            collection.bulk_write(operations)

        return redirect(url_for('scraper.results', collection_name=query))

    return render_template('index.html', form=form, items=items, collections=collections)


@scraper_bp.route('/select_collection', methods=['GET'])
def select_collection():
    collections = db.list_collection_names()
    return render_template('select_collection.html', collections=collections)


@scraper_bp.route('/results/<collection_name>', methods=['GET', 'POST'])
def results(collection_name):
    collection = db[collection_name]
    form = FilterForm()
    query = {}
    sort = [("price_value", 1)]

    if request.method == 'POST' and form.validate():
        min_price = form.min_price.data
        max_price = form.max_price.data
        sort_order = form.sort_order.data

        if min_price is not None:
            query['price_value'] = {'$gte': min_price}
        if max_price is not None:
            if 'price_value' in query:
                query['price_value']['$lte'] = max_price
            else:
                query['price_value'] = {'$lte': max_price}
        if sort_order == 'desc':
            sort = [("price_value", -1)]

    items = list(collection.find(query).sort(sort))

    return render_template('results.html', items=items, collection_name=collection_name, form=form)
