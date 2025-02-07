from flask import Flask, render_template, url_for, request, redirect
from meals import Meals, MealsStore
from orders import Orders, OrdersStore
import datetime


class ReverseProxied():
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME3', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)


app = Flask(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app)


dummy_meals = [
    Meals(
        1,
        'Pizza',
        [
            'Tomato sauce',
            'Green olives sliced',
            'Steaks',
            'Cheese Almstazarila'
        ],
        'https://images.pexels.com/photos/1069449/pexels-photo-1069449.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940',
        8
    ),
    Meals(
        2,
        'Hamburger',
        [
            'Minced meat',
            'Onion slices',
            'Chesar cheese',
            'Sliced Tomatoes',
            'Lettuce',
            'Filled with French fries and Ketchup sauce'
        ],
        'https://images.pexels.com/photos/19642/pexels-photo.jpg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940',
        5
    ),
    Meals(
        3,
        'French Burger',
        [
            'Minced meat',
            'Onion slices ',
            'Sliced tomatoes',
            'Letuce',
            'Pickle',
            'Tahina',
            'Mint'
        ],
        'https://images.pexels.com/photos/47725/hamburger-food-meal-tasty-47725.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940',
        3
    ),
    Meals(
        4,
        'Veg Sandwich',
        [
            'Toast bread',
            'Chicken breast slices',
            'Letuce',
            'Spices'
        ],
        'https://images.pexels.com/photos/1647163/pexels-photo-1647163.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940',
        6
    ),
    Meals(
        5,
        'Simple Pizza',
        [
            'Tomatoes sauce',
            'Olive oil',
            'Wild thyme',
            'Mayonnaise'
        ],
        'https://images.pexels.com/photos/1069450/pexels-photo-1069450.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940',
        2
    ),
    Meals(
        6,
        'Sandwich',
        [
            'Baked bread in medium size',
            'Grilled meat',
            'Colored pepper',
            'Pickle',
            'Mayonnaise'
        ],
        'https://images.pexels.com/photos/1603898/pexels-photo-1603898.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940',
        4
    ),
    Meals(
        7,
        'Leg chicken',
        [
            'Minced garlic',
            'Fish sauce',
            'Soy sauce',
            'Spicy grated ginger',
            'Hot sauce',
            'Cruched corn flakes'
        ],
        'https://images.pexels.com/photos/60616/fried-chicken-chicken-fried-crunchy-60616.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940',
        5
    ),
    Meals(
        8,
        'Fried meat',
        [
            'Sheep meat slices',
            'Powder muffins',
            'Curry',
            'Spices of sheep meat',
            'Turmeric'
        ],
        'https://images.pexels.com/photos/991967/pexels-photo-991967.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940',
        9
    )

]

meals = MealsStore(dummy_meals)
meals.get_all()

dummy_orders = []
orders = OrdersStore(dummy_orders)
orders.add(Orders(1, dummy_meals[0], 3, 'Adel', 'my address', 'today'))
orders.get_all()


@app.route('/')
def index():
    title = 'Adelara fast-food chef'
    return render_template('meals.html', admin=False, meals=dummy_meals, title=title)

@app.route('/admin')
def admin_role():
    title = 'Adelara fast-food chef'
    return render_template('meals.html', admin=True, meals=dummy_meals, title=title)


@app.route('/404')
def oops():
    title = "Oops"
    return render_template('404.html' ,title=title)


app.current_id = 1
@app.route('/details/<int:id>', methods=["GET", "POST"])
def details(id):
    meal = meals.get_details(id)
    title = 'Adelara|Meal details'

    if hasattr(meal, 'id'):
        if request.method == "GET":
            return render_template('details.html', meal=meal, title=title)

        elif request.method == "POST":
            new_order = Orders(id=app.current_id,
                               meal=meal,
                               quantity=int(request.form["quantity"]),
                               user=request.form["user"],
                               address=request.form["address"],
                               date=datetime.datetime.now().strftime("%m/%d/%Y at %H:%M:%S")
                               )
            app.current_id += 1
            orders.add(new_order)
            orders.get_all()
            return render_template("success.html", order=new_order)

    else:
        return redirect(url_for('oops'))


@app.route('/orders')
def list_orders():
    title = 'Adelara|Order'
    return render_template('orders.html', orders=dummy_orders, title=title)


@app.route('/add/meal', methods=["GET", "POST"])
def add_meal():
    title = 'Adelara|Add new meal'
    last_meal_id = dummy_meals[-1].id
    if request.method == "POST":
        last_meal_id += 1
        ings = request.form.getlist("ings[]")
        new_meal = Meals(id=last_meal_id,
                         name=request.form["name"],
                         descr=ings,
                         photo_url=request.form["photo"],
                         price=int(request.form["price"])
                         )
        meals.add(new_meal)
        meals.get_all()
        return redirect(url_for("admin_role"))

    elif request.method == "GET":
        return render_template('add-meal.html', title=title)


@app.route('/remove/meal<int:id>')
def meal_remove(id):
    meals.remove(id)
    return redirect(url_for("admin_role"))


@app.route('/update/meal/<int:id>', methods=["GET", "POST"])
def meal_update(id):
    if request.method == 'POST':
        ings = request.form.getlist("ings[]")
        update_fields = {
            'name': request.form['name'],
            'descr': ings,
            'photo_url': request.form['photo'],
            'price': int(request.form['price'])
        }

        meals.update(id, update_fields)

        return redirect(url_for("admin_role"))
    elif request.method == 'GET':
        meal = meals.get_details(id)
        title = 'Adelara|Update '+meal.name
        return render_template('update-meal.html', meal=meal, title=title)


@app.route('/sw.js', methods=['GET'])
def sw():
    return app.send_static_file('sw.js')