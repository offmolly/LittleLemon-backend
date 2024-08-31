# Api details:

## Intro
This is a simple REST API for 'little lemon' restaurant made using Django using sqllite as a database. This was created as a capstone project for Meta Backend Developer Course.

Users with different roles can browse, add and edit menu items, place orders, browse orders, assign delivery crew to orders and set delivery order status.

## Structure
### User roles
* Admin
* Manager
* Delivery Crew
* No role = Customer

### Authentication
* Created using Djoser
* Token and session authentication enabled
* Id Feild : username (pk)

### Throttle
* Limits Api requests
* Created using rest_framework.throttling
* Throttle Rate:
  * Anon: 2/min
  * User: 10/min

## Database Schema
* Tables:
  * Category: id, slug, title
  * MenuItem: id, title, price, featured, category_id
  * Cart: id, user_id, menuitem_id, quantity, unit_price, price
  * Order: id, user_id, delivery_crew_id, status, total, date
  * OrderItem: id, order_id, menuitem_id, quantity, unit_price, price

* Relationships:
  * A Category can have many MenuItems (One-to-Many).
  * A MenuItem belongs to one Category (Many-to-One).
  * A User can have many Cart items and many Orders (One-to-Many).
  * A Cart item belongs to one User and references one MenuItem (Many-to-One).
  * An Order belongs to one User and can optionally have one User assigned as the delivery crew (One-to-Many, nullable).
  * An Order can have many OrderItems (One-to-Many).
  * An OrderItem belongs to one Order and references one MenuItem (Many-to-One).

* Additional Notes:
  * The schema uses appropriate data types for each field based on Django model definitions.
  * Indexes are added to columns that are frequently queried (e.g., title, price, user_id) for faster performance.

## Endpoints
* **{user groups & user creatioin}**
  * /api/users: 
    >creates a new user with password, email and username
  */api/users/me: 
    >Displays the current user
  * /api/token/login: 
    >Get a token with username and password

  * /api/groups/manager/users:
    >* Get: Returns all managers
    >* Post,Delete: Assigns or Deletes the user in the payload to the manager group and returns 201-Created

  * /api/groups/delivery-crew/users:
    >* Get: Returns all delivery Crew
    >* Post: Assigns or Deletes the user in the payload to delivery crew group

* **{menu-item}**
  * /api/menu-items:
    >* Get: displays all menu items to customer
    >* Post,Put,Delete:  add,edit or remove items, 403 Unauthorized for users that are not  Manager or Admin 

  * /api/menu-items/{menuItem}:
    >* GET: displays single item
    >* Put,Delete: edit or remove selected item, 403 Unauthorized for users that are not  Manager or Admin

* **{cart}**
  * /api/cart/menu-items:
    >* Get: returns all current items in cart for user
    >* Post: Adds menuitems to the cart sets the authenticated user as the user id of the cart items
    >* Delete: delets all the menu items created by the current user

* **{Order}**
  * /api/orders:
    >* Get: returns all orders with order items created by the user. Only managers can see all orders. If a delivery-crew               visits orders, returns all order items assigned to the crew.
    >* Post: creates a new order item for customer, gets current cart items from cart endpoints and adds them to order                   items table, then deletes the cart for user.
    >* Patch: Delivery Crew can set the status of the order to 0 or 1, and can update noting else.

  * /api/orders/{orderId}
    >* Get: returns items for the current id for customers.
    >* Put,Patch: Updates the order. Manager can use this to assign delivery crew and update order status to 0 or 1.
    >* Delete: Only managers can delete this order. 


## Test Users
Tested using Insomnia api client. go to ***api/users*** to create a user. then ***api/token/login*** to get auth token.
Login to admin page as superuser by going to ***loacalhost:/admin*** to access all models.

### Superuser
    username: admin
    password: admin@lemon
    
### Manager
    username: Maria
    password: maria@lemon

### Delivery Crew
    username: rider
    password: rider@lemon

### Customer
    username: cole
    password: cole1234
