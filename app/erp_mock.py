"""
Mock ERP System (Προσομοίωση Εξωτερικού ERP API της Επιχείρησης)
Στην πραγματικότητα, αυτές οι συναρτήσεις θα έκαναν HTTP requests (requests.get/post)
στα API endpoints του ERP του πελάτη (π.χ. https://api.softone.gr/v1/...)
"""

from datetime import datetime

# Εικονική Βάση Δεδομένων του ERP (Όπως υπάρχει ήδη στον πελάτη)
ERP_DATABASE = {
    "products": [
        {"sku": "OIL-01", "name": "Ελαιόλαδο 1L", "stock": 120, "price": 8.50, "expiration": "2027-12-31"},
        {"sku": "HON-01", "name": "Μέλι Θυμαρίσιο 1kg", "stock": 45, "price": 12.00, "expiration": "2026-11-20"},
        {"sku": "CHS-01", "name": "Φέτα ΠΟΠ 500g", "stock": 30, "price": 6.20, "expiration": "2026-08-15"},
        {"sku": "OUZ-01", "name": "Ούζο 700ml", "stock": 80, "price": 9.80, "expiration": "2028-05-10"},
        {"sku": "OLV-01", "name": "Ελιές Καλαμών 500g", "stock": 65, "price": 4.10, "expiration": "2027-03-30"},
    ],
    "invoices": [
        {"id": "INV-1001", "customer": "Αλφα Α.Ε.", "amount": 450.00, "date": "2026-11-01", "status": "PAID"},
        {"id": "INV-1002", "customer": "Βήτα Μαρκέτ", "amount": 1280.50, "date": "2026-11-05", "status": "PAID"}
    ]
}

# --- ERP API ENDPOINTS (READ / WRITE) ---

def erp_get_inventory():
    """Επιστρέφει την πλήρη εικόνα αποθήκης από το ERP."""
    return ERP_DATABASE["products"]

def erp_search_product(sku: str):
    """Αναζητά ένα συγκεκριμένο προϊόν στο ERP βάσει SKU."""
    for prod in ERP_DATABASE["products"]:
        if prod["sku"].upper() == sku.upper():
            return prod
    return None

def erp_create_sales_invoice(customer_name: str, sku: str, quantity: int):
    """Εκτελεί πώληση στο ERP: Μειώνει το stock και εκδίδει τιμολόγιο."""
    prod = erp_search_product(sku)
    if not prod:
        return {"success": False, "error": f"Το προϊόν με SKU '{sku}' δεν βρέθηκε στο ERP."}
    
    if prod["stock"] < quantity:
        return {"success": False, "error": f"Ανεπαρκές απόθεμα στο ERP. Διαθέσιμα: {prod['stock']} τμχ."}

    # Ενημέρωση ERP
    prod["stock"] -= quantity
    total_amount = quantity * prod["price"]
    inv_id = f"INV-{1003 + len(ERP_DATABASE['invoices'])}"
    
    new_invoice = {
        "id": inv_id,
        "customer": customer_name,
        "amount": total_amount,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "status": "PAID"
    }
    ERP_DATABASE["invoices"].append(new_invoice)

    return {
        "success": True,
        "invoice_id": inv_id,
        "customer": customer_name,
        "product": prod["name"],
        "quantity_sold": quantity,
        "total_amount": total_amount,
        "remaining_stock": prod["stock"]
    }

def erp_get_invoices_summary():
    """Επιστρέφει τα στατιστικά τιμολογίων από το ERP."""
    invoices = ERP_DATABASE["invoices"]
    total_sum = sum(inv["amount"] for inv in invoices)
    return {
        "total_count": len(invoices),
        "total_sum": total_sum,
        "invoices": invoices
    }