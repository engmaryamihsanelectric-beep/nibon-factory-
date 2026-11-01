import sys
import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

class NipponSystemApp:
    def __init__(self, root):
        self.root = root
        self.root.title("نظام إدارة وحسابات مصنع نيبون - Nippon Accounting System")
        self.root.geometry("1150x700")
        
        # Enable Right-to-Left styling feel & colors
        self.bg_color = "#F4F6F9"
        self.primary_color = "#1F497D"
        self.accent_color = "#DCE6F1"
        self.root.configure(bg=self.bg_color)
        
        # Database Initialization
        self.conn = sqlite3.connect("nippon_factory.db")
        self.init_db()
        
        # Header Frame
        header = tk.Frame(self.root, bg=self.primary_color, height=60)
        header.pack(fill=tk.X, side=tk.TOP)
        title_lbl = tk.Label(header, text="برنامج حسابات وإدارة مصنع نيبون (Nippon)", font=("Segoe UI", 16, "bold"), fg="white", bg=self.primary_color)
        title_lbl.pack(pady=12)
        
        # Notebook (Tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create Tabs
        self.tab_dashboard = ttk.Frame(self.notebook)
        self.tab_sales = ttk.Frame(self.notebook)
        self.tab_inventory = ttk.Frame(self.notebook)
        self.tab_production = ttk.Frame(self.notebook)
        self.tab_expenses = ttk.Frame(self.notebook)
        self.tab_setup = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_dashboard, text=" 📊 لوحة التحكم والأرباح ")
        self.notebook.add(self.tab_sales, text=" 💰 المبيعات والديون ")
        self.notebook.add(self.tab_inventory, text=" 📦 إدارة المخزن ")
        self.notebook.add(self.tab_production, text=" ⚙️ حركة الإنتاج ")
        self.notebook.add(self.tab_expenses, text=" 📝 المصروفات والرواتب ")
        self.notebook.add(self.tab_setup, text=" ⚙️ البيانات الأساسية ")
        
        self.build_setup_tab()
        self.build_inventory_tab()
        self.build_sales_tab()
        self.build_expenses_tab()
        self.build_dashboard_tab()
        
    def init_db(self):
        cur = self.conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY, name TEXT, phone TEXT, address TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS suppliers (id INTEGER PRIMARY KEY, name TEXT, phone TEXT, item TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS inventory_in (id INTEGER PRIMARY KEY, date TEXT, supplier TEXT, item TEXT, qty REAL, price REAL, total REAL)")
        cur.execute("CREATE TABLE IF NOT EXISTS sales (id INTEGER PRIMARY KEY, inv_no TEXT, date TEXT, customer TEXT, product TEXT, qty REAL, price REAL, total REAL, pay_type TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY, date TEXT, customer TEXT, amount REAL, notes TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS expenses (id INTEGER PRIMARY KEY, date TEXT, item TEXT, category TEXT, amount REAL, notes TEXT)")
        
        # Insert sample defaults if empty
        cur.execute("SELECT COUNT(*) FROM customers")
        if cur.fetchone()[0] == 0:
            cur.executemany("INSERT INTO customers (name, phone, address) VALUES (?,?,?)", [
                ("معرض الأمل", "07501234567", "دهوك - السوق"),
                ("شركة البركة", "07507654321", "كواشي"),
                ("محلات النور", "07509876543", "دهوك - المركز")
            ])
            cur.executemany("INSERT INTO suppliers (name, phone, item) VALUES (?,?,?)", [
                ("شركة السلام للتوريد", "07501112233", "نيلون خام"),
                ("شركة العالمية للبلاستيك", "07504445566", "مواد خام")
            ])
            cur.executemany("INSERT INTO sales (inv_no, date, customer, product, qty, price, total, pay_type) VALUES (?,?,?,?,?,?,?,?)", [
                ("INV-1001", "2026-11-01", "معرض الأمل", "أكياس نفايات (حجم كبير)", 1.5, 1600.0, 2400.0, "آجل"),
                ("INV-1002", "2026-11-03", "شركة البركة", "أكياس نفايات (حجم وسط)", 2.5, 1650.0, 4125.0, "آجل")
            ])
            cur.executemany("INSERT INTO payments (date, customer, amount, notes) VALUES (?,?,?,?)", [
                ("2026-11-05", "معرض الأمل", 1000.0, "دفعة نقداً")
            ])
            cur.executemany("INSERT INTO expenses (date, item, category, amount, notes) VALUES (?,?,?,?,?)", [
                ("2026-11-02", "كهرباء ومولدة", "تشغيل", 350.0, "وقود المولدة"),
                ("2026-11-04", "رواتب عمال", "أجور", 850.0, "أجور أسبوعية")
            ])
            cur.executemany("INSERT INTO inventory_in (date, supplier, item, qty, price, total) VALUES (?,?,?,?,?,?)", [
                ("2026-11-01", "شركة السلام للتوريد", "نيلون خام", 10.0, 1200.0, 12000.0)
            ])
        self.conn.commit()

    def build_setup_tab(self):
        lbl = ttk.Label(self.tab_setup, text="إدارة العملاء والموردين", font=("Segoe UI", 12, "bold"))
        lbl.pack(pady=10)
        
        frame = ttk.Frame(self.tab_setup)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Customers Table
        tree_cust = ttk.Treeview(frame, columns=("ID", "Name", "Phone", "Address"), show="headings", height=8)
        tree_cust.heading("ID", text="م")
        tree_cust.heading("Name", text="اسم العميل / المحل")
        tree_cust.heading("Phone", text="رقم الهاتف")
        tree_cust.heading("Address", text="العنوان")
        tree_cust.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=5)
        
        cur = self.conn.cursor()
        for row in cur.execute("SELECT * FROM customers"):
            tree_cust.insert("", tk.END, values=row)

    def build_inventory_tab(self):
        frame = ttk.Frame(self.tab_inventory)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        lbl = ttk.Label(frame, text="حركة المشتريات والمواد الخام (الوارد)", font=("Segoe UI", 12, "bold"))
        lbl.pack(anchor=tk.E, pady=5)
        
        tree_inv = ttk.Treeview(frame, columns=("Date", "Supplier", "Item", "Qty", "Price", "Total"), show="headings", height=10)
        tree_inv.heading("Date", text="التاريخ")
        tree_inv.heading("Supplier", text="المورد")
        tree_inv.heading("Item", text="الصنف")
        tree_inv.heading("Qty", text="الكمية (طن)")
        tree_inv.heading("Price", text="سعر الطن ($)")
        tree_inv.heading("Total", text="الإجمالي ($)")
        tree_inv.pack(fill=tk.BOTH, expand=True)
        
        cur = self.conn.cursor()
        for row in cur.execute("SELECT date, supplier, item, qty, price, total FROM inventory_in"):
            tree_inv.insert("", tk.END, values=row)

    def build_sales_tab(self):
        frame = ttk.Frame(self.tab_sales)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        lbl = ttk.Label(frame, text="سجل المبيعات والديون المستحقة", font=("Segoe UI", 12, "bold"))
        lbl.pack(anchor=tk.E, pady=5)
        
        tree_sales = ttk.Treeview(frame, columns=("Inv", "Date", "Customer", "Product", "Qty", "Price", "Total", "PayType"), show="headings", height=10)
        tree_sales.heading("Inv", text="رقم الفاتورة")
        tree_sales.heading("Date", text="التاريخ")
        tree_sales.heading("Customer", text="العميل")
        tree_sales.heading("Product", text="المنتج")
        tree_sales.heading("Qty", text="الكمية (طن)")
        tree_sales.heading("Price", text="السعر")
        tree_sales.heading("Total", text="الإجمالي ($)")
        tree_sales.heading("PayType", text="نوع الدفع")
        tree_sales.pack(fill=tk.BOTH, expand=True)
        
        cur = self.conn.cursor()
        for row in cur.execute("SELECT inv_no, date, customer, product, qty, price, total, pay_type FROM sales"):
            tree_sales.insert("", tk.END, values=row)

    def build_expenses_tab(self):
        frame = ttk.Frame(self.tab_expenses)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        lbl = ttk.Label(frame, text="سجل المصروفات التشغيلية والرواتب", font=("Segoe UI", 12, "bold"))
        lbl.pack(anchor=tk.E, pady=5)
        
        tree_exp = ttk.Treeview(frame, columns=("Date", "Item", "Cat", "Amount", "Notes"), show="headings", height=10)
        tree_exp.heading("Date", text="التاريخ")
        tree_exp.heading("Item", text="بند المصروف")
        tree_exp.heading("Cat", text="الفئة")
        tree_exp.heading("Amount", text="المبلغ ($)")
        tree_exp.heading("Notes", text="التفاصيل")
        tree_exp.pack(fill=tk.BOTH, expand=True)
        
        cur = self.conn.cursor()
        for row in cur.execute("SELECT date, item, category, amount, notes FROM expenses"):
            tree_exp.insert("", tk.END, values=row)

    def build_dashboard_tab(self):
        frame = ttk.Frame(self.tab_dashboard)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        cur = self.conn.cursor()
        cur.execute("SELECT SUM(total) FROM sales")
        total_sales = cur.fetchone()[0] or 0.0
        
        cur.execute("SELECT SUM(amount) FROM expenses")
        total_exp = cur.fetchone()[0] or 0.0
        
        cur.execute("SELECT SUM(total) FROM inventory_in")
        total_raw = cur.fetchone()[0] or 0.0
        
        net_profit = total_sales - total_exp
        
        # Summary Cards
        cards_frame = ttk.Frame(frame)
        cards_frame.pack(fill=tk.X, pady=10)
        
        card1 = tk.Label(cards_frame, text=f"إجمالي المبيعات\n${total_sales:,.2f}", font=("Segoe UI", 12, "bold"), bg="#D4EDDA", fg="#155724", width=22, height=4, relief=tk.GROOVE)
        card1.pack(side=tk.LEFT, padx=10)
        
        card2 = tk.Label(cards_frame, text=f"إجمالي المصروفات\n${total_exp:,.2f}", font=("Segoe UI", 12, "bold"), bg="#F8D7DA", fg="#721C24", width=22, height=4, relief=tk.GROOVE)
        card2.pack(side=tk.LEFT, padx=10)
        
        card3 = tk.Label(cards_frame, text=f"صافي الأرباح\n${net_profit:,.2f}", font=("Segoe UI", 12, "bold"), bg="#CCE5FF", fg="#004085", width=22, height=4, relief=tk.GROOVE)
        card3.pack(side=tk.LEFT, padx=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = NipponSystemApp(root)
    root.mainloop()
