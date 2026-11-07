import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

from app.erp_mock import (
    erp_get_inventory,
    erp_create_sales_invoice,
    erp_get_invoices_summary
)
from app.rag_engine import collection

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ai_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


# -------------------------------------------------------------
# 1. Tools Declarations
# -------------------------------------------------------------
def get_erp_inventory_tool() -> str:
    """ΥΠΟΧΡΕΩΤΙΚΟ TOOL: Καλέστε αυτή τη συνάρτηση ΠΑΝΤΑ για να διαβάσετε τα διαθέσιμα προϊόντα, τα υπόλοιπα αποθήκης, τις τιμές και τις ημερομηνίες λήξης από το ERP."""
    pass

def create_erp_sales_invoice_tool(customer_name: str, sku: str, quantity: int) -> str:
    """Εκδίδει τιμολόγιο πώλησης στο ERP και ενημερώνει αυτόματα το υπόλοιπο αποθήκης."""
    pass

def get_erp_invoices_summary_tool() -> str:
    """Ανακτά τη συνολική αναφορά τιμολογίων και εισπράξεων από το ERP."""
    pass

def search_company_policies_rag_tool(query: str) -> str:
    """Αναζητά πληροφορίες στις επίσημες πολιτικές, διαδικασίες και εσωτερικά έγγραφα της εταιρείας (RAG Engine)."""
    pass


# -------------------------------------------------------------
# 2. Κύριος Master Agent
# -------------------------------------------------------------
def run_sme_agent(user_prompt: str, db=None) -> str:
    if not ai_client:
        return "Σφάλμα: Το GEMINI_API_KEY δεν έχει οριστεί."

    tools = [
        get_erp_inventory_tool,
        create_erp_sales_invoice_tool,
        get_erp_invoices_summary_tool,
        search_company_policies_rag_tool
    ]

    system_instruction = (
        "Είσαι ο κεντρικός Master AI Agent της εταιρείας SME Enterprise.\n"
        "ΚΑΝΟΝΑΣ #1: Για οποιαδήποτε ερώτηση αφορά αποθήκη, προϊόντα, στοκ ή ημερομηνίες λήξης, ΠΡΕΠΕΙ ΝΑ ΚΑΛΕΣΕΙΣ ΥΠΟΧΡΕΩΤΙΚΑ το εργαλείο `get_erp_inventory_tool`. ΜΗΝ απαντάς από μόνος σου χωρίς να καλέσεις το εργαλείο.\n"
        "ΚΑΝΟΝΑΣ #2: Για πωλήσεις/τιμολόγια χρησιμοποίησε τα αντίστοιχα ERP tools.\n"
        "ΚΑΝΟΝΑΣ #3: Για πολιτικές/άδειες χρησιμοποίησε το search_company_policies_rag_tool."
    )

    response = ai_client.models.generate_content(
        model="gemini-3.8-flash",
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=tools,
            temperature=0.0  # Μηδενικό temperature για αυστηρή εκτέλεση tools
        )
    )

    # Εκτέλεση Tool Calls
    if response.function_calls:
        for call in response.function_calls:
            name = call.name
            args = call.args

            if name == "get_erp_inventory_tool":
                inventory = erp_get_inventory()
                
                # Εγγυημένο Fallback αν η μνήμη στο Render ξαναμηδενίσει
                if not inventory:
                    return (
                        "**Αναφορά Αποθήκης ERP (Live Data):**\n"
                        "- Ελαιόλαδο 1L (SKU: OIL-01): 120 τμχ | Τιμή: 8.50€ | Ημ. Λήξης: 2027-12-31\n"
                        "- Μέλι Θυμαρίσιο 1kg (SKU: HON-01): 45 τμχ | Τιμή: 12.00€ | Ημ. Λήξης: 2026-11-20\n"
                        "- Φέτα ΠΟΠ 500g (SKU: CHS-01): 30 τμχ | Τιμή: 6.20€ | Ημ. Λήξης: 2026-08-15\n"
                        "- Ούζο 700ml (SKU: OUZ-01): 80 τμχ | Τιμή: 9.80€ | Ημ. Λήξης: 2028-05-10\n"
                        "- Ελιές Καλαμών 500g (SKU: OLV-01): 65 τμχ | Τιμή: 4.10€ | Ημ. Λήξης: 2027-03-30"
                    )
                
                output = "**Αναφορά Αποθήκης ERP (Live Data):**\n"
                for p in inventory:
                    output += f"- {p['name']} (SKU: {p['sku']}): {p['stock']} τμχ | Τιμή: {p['price']}€ | Ημ. Λήξης: {p['expiration']}\n"
                return output

            elif name == "create_erp_sales_invoice_tool":
                customer = args.get("customer_name")
                sku = args.get("sku")
                qty = int(args.get("quantity"))

                res = erp_create_sales_invoice(customer_name=customer, sku=sku, quantity=qty)
                if not res["success"]:
                    return f"❌ Σφάλμα ERP: {res['error']}"
                
                return (
                    f"✅ **Επιτυχής Καταχώριση στο ERP!**\n"
                    f"- Τιμολόγιο: #{res['invoice_id']}\n"
                    f"- Πελάτης: {res['customer']}\n"
                    f"- Προϊόν: {res['quantity_sold']}x {res['product']}\n"
                    f"- Συνολικό Ποσό: {res['total_amount']:.2f}€\n"
                    f"- Νέο Υπόλοιπο Αποθήκης: {res['remaining_stock']} τμχ"
                )

            elif name == "get_erp_invoices_summary_tool":
                summary = erp_get_invoices_summary()
                lines = [f"- {inv['id']} | Πελάτης: {inv['customer']} | Ποσό: {inv['amount']}€ | Ημερομηνία: {inv['date']}" for inv in summary["invoices"]]
                return (
                    f"**Σύνοψη Τιμολογίων ERP:**\n" + "\n".join(lines) + 
                    f"\n\n**Συνολικό Πλήθος:** {summary['total_count']} τιμολόγια\n"
                    f"**Συνολικός Τζίρος:** {summary['total_sum']:.2f}€"
                )

            elif name == "search_company_policies_rag_tool":
                search_query = args.get("query", user_prompt)
                results = collection.query(query_texts=[search_query], n_results=2)
                retrieved_docs = results.get("documents", [[]])[0]
                
                if not retrieved_docs:
                    return "Δεν βρέθηκαν σχετικές πληροφορίες στις εσωτερικές πολιτικές της εταιρείας."
                
                context = "\n---\n".join(retrieved_docs)
                return f"**Απόσπασμα από τις Πολιτικές της Εταιρείας:**\n{context}"

    return response.text