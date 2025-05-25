import uuid

class Product:
    """
    Represents a product in the inventory.
    """
    def __init__(self, product_id: str, name: str, description: str, price: float, quantity: int):
        if not product_id:
            raise ValueError("Product ID cannot be empty.")
        if not name:
            raise ValueError("Product name cannot be empty.")
        if price <= 0:
            raise ValueError("Price must be positive.")
        if quantity < 0:
            raise ValueError("Quantity cannot be negative.")

        self.product_id = product_id
        self.name = name
        self.description = description
        self.price = price
        self.quantity = quantity

    def __str__(self):
        return (f"ID: {self.product_id}, Name: {self.name}, "
                f"Price: ${self.price:.2f}, Quantity: {self.quantity}\n"
                f"  Description: {self.description}")

    def update_details(self, name: str = None, description: str = None, price: float = None):
        """Updates product details. Only provided fields are updated."""
        if name is not None:
            if not name:
                raise ValueError("Product name cannot be empty.")
            self.name = name
        if description is not None:
            self.description = description
        if price is not None:
            if price <= 0:
                raise ValueError("Price must be positive.")
            self.price = price

    def update_quantity(self, quantity_change: int):
        """
        Updates the quantity of the product.
        A positive value for quantity_change means stock in.
        A negative value for quantity_change means stock out.
        """
        new_quantity = self.quantity + quantity_change
        if new_quantity < 0:
            raise ValueError(f"Cannot stock out {abs(quantity_change)} items. "
                             f"Only {self.quantity} items available for '{self.name}'.")
        self.quantity = new_quantity


class InventoryManager:
    """
    Manages the inventory of products.
    Implemented as a Singleton.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(InventoryManager, cls).__new__(cls)
            cls._instance._products = {}  # Initialize inventory storage
        return cls._instance

    def add_product(self, product: Product) -> bool:
        """Adds a product to the inventory."""
        if product.product_id in self._products:
            print(f"Error: Product with ID '{product.product_id}' already exists.")
            return False
        self._products[product.product_id] = product
        print(f"Product '{product.name}' added successfully.")
        return True

    def remove_product(self, product_id: str) -> bool:
        """Removes a product from the inventory by its ID."""
        if product_id not in self._products:
            print(f"Error: Product with ID '{product_id}' not found.")
            return False
        removed_product_name = self._products[product_id].name
        del self._products[product_id]
        print(f"Product '{removed_product_name}' (ID: {product_id}) removed successfully.")
        return True

    def get_product(self, product_id: str) -> Product | None:
        """Retrieves a product by its ID."""
        product = self._products.get(product_id)
        if not product:
            print(f"Error: Product with ID '{product_id}' not found.")
        return product

    def update_product_details(self, product_id: str, name: str = None,
                               description: str = None, price: float = None) -> bool:
        """Updates the details of an existing product."""
        product = self.get_product(product_id)
        if product:
            try:
                product.update_details(name, description, price)
                print(f"Product ID '{product_id}' details updated successfully.")
                return True
            except ValueError as e:
                print(f"Error updating product: {e}")
                return False
        return False

    def update_stock(self, product_id: str, quantity_change: int) -> bool:
        """
        Updates the stock quantity of a product.
        Positive quantity_change for stock in, negative for stock out.
        """
        product = self.get_product(product_id)
        if product:
            try:
                product.update_quantity(quantity_change)
                action = "stocked in" if quantity_change > 0 else "stocked out"
                print(f"{abs(quantity_change)} units of '{product.name}' (ID: {product_id}) {action}. "
                      f"New quantity: {product.quantity}.")
                return True
            except ValueError as e:
                print(f"Error updating stock: {e}")
                return False
        return False

    def list_all_products(self):
        """Lists all products in the inventory."""
        if not self._products:
            print("Inventory is currently empty.")
            return
        print("\n--- Current Inventory ---")
        for product_id, product in self._products.items(): # Consider using product directly
            print(f"ID: {product.product_id}, Name: {product.name}, "
                  f"Price: ${product.price:.2f}, Quantity: {product.quantity}")
        print("-------------------------\n")

# --- Helper Functions for CLI ---
def generate_unique_id() -> str:
    """Generates a short unique ID."""
    return str(uuid.uuid4().hex)[:8]

def get_product_id_input(prompt_message: str) -> str:
    """Gets product ID from user."""
    return input(prompt_message)

# --- CLI Handler Functions ---
def handle_add_product(inventory: InventoryManager):
    print("\n--- Add New Product ---")
    prod_id = input("Enter Product ID (leave blank to auto-generate): ")
    if not prod_id:
        prod_id = generate_unique_id()
        print(f"Generated Product ID: {prod_id}")
    name = input("Enter Product Name: ")
    description = input("Enter Product Description: ")
    price = float(input("Enter Product Price: "))
    quantity = int(input("Enter Product Quantity: "))
    product = Product(prod_id, name, description, price, quantity)
    inventory.add_product(product)

def handle_remove_product(inventory: InventoryManager):
    print("\n--- Remove Product ---")
    prod_id = get_product_id_input("Enter Product ID to remove: ")
    inventory.remove_product(prod_id)

def handle_view_product(inventory: InventoryManager):
    print("\n--- View Product Details ---")
    prod_id = get_product_id_input("Enter Product ID to view: ")
    product = inventory.get_product(prod_id)
    if product:
        print(product)

def handle_update_product_details(inventory: InventoryManager):
    print("\n--- Update Product Details ---")
    prod_id = get_product_id_input("Enter Product ID to update: ")
    if inventory.get_product(prod_id):  # Check if product exists first
        name = input("Enter new Name (or leave blank to keep current): ") or None
        description = input("Enter new Description (or leave blank to keep current): ") or None
        price_str = input("Enter new Price (or leave blank to keep current): ")
        price = float(price_str) if price_str else None
        inventory.update_product_details(prod_id, name, description, price)

def handle_stock_in(inventory: InventoryManager):
    print("\n--- Stock In ---")
    prod_id = get_product_id_input("Enter Product ID to stock in: ")
    if inventory.get_product(prod_id):
        amount_str = input("Enter quantity to add: ")
        if not amount_str.isdigit() or int(amount_str) <=0: # Basic validation
            print("Error: Quantity to add must be a positive integer.")
            return
        amount = int(amount_str)
        inventory.update_stock(prod_id, amount)


def handle_stock_out(inventory: InventoryManager):
    print("\n--- Stock Out ---")
    prod_id = get_product_id_input("Enter Product ID to stock out: ")
    if inventory.get_product(prod_id):
        amount_str = input("Enter quantity to remove: ")
        if not amount_str.isdigit() or int(amount_str) <=0: # Basic validation
            print("Error: Quantity to remove must be a positive integer.")
            return
        amount = int(amount_str)
        inventory.update_stock(prod_id, -amount) # Negative for stock out

def handle_list_all_products(inventory: InventoryManager):
    inventory.list_all_products()

def handle_exit():
    print("Exiting Inventory Management System. Goodbye!")
    return False # Signal to stop the main loop

def display_menu():
    print("\nInventory Management System")
    print("1. Add New Product")
    print("2. Remove Product")
    print("3. View Product Details")
    print("4. Update Product Details")
    print("5. Stock In (Increase Quantity)")
    print("6. Stock Out (Decrease Quantity)")
    print("7. List All Products")
    print("8. Exit")

# --- Main Menu using Dispatch Table ---
def main_menu(inventory: InventoryManager):
    """Displays the main menu and handles user input using a dispatch table."""

    menu_actions = {
        '1': handle_add_product,
        '2': handle_remove_product,
        '3': handle_view_product,
        '4': handle_update_product_details,
        '5': handle_stock_in,
        '6': handle_stock_out,
        '7': handle_list_all_products,
        '8': handle_exit
    }

    running = True
    while running:
        display_menu()
        choice = input("Enter your choice (1-8): ")
        action = menu_actions.get(choice)

        try:
            if action:
                if choice == '8': # Special handling for exit to stop loop
                    running = action()
                else:
                    action(inventory) # Call the appropriate handler
            else:
                print("Invalid choice. Please enter a number between 1 and 8.")

        except ValueError as ve:
            print(f"Input Error: {ve}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

        if running: # Avoid "Press Enter to continue..." if exiting
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    inventory_manager1 = InventoryManager()
    inventory_manager2 = InventoryManager()

    print(f"Is inventory_manager1 the same instance as inventory_manager2? {inventory_manager1 is inventory_manager2}\n")

    try:
        prod1 = Product(product_id="LPT001", name="Laptop X1", description="High-performance laptop", price=1200.99, quantity=10)
        prod2 = Product(product_id="MSE002", name="Wireless Mouse", description="Ergonomic wireless mouse", price=25.50, quantity=50)
        inventory_manager1.add_product(prod1)
        inventory_manager1.add_product(prod2)
    except ValueError as e:
        print(f"Error during pre-population: {e}")

    main_menu(inventory_manager1)