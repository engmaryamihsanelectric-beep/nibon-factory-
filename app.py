import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# إعدادات صفحة الويب
st.set_page_config(
    page_title="مصنع نيبون - نظام الحسابات",
    page_icon="🏭",
    layout="wide"
)

# الاتصال بقاعدة البيانات
conn = sqlite3.connect("nippon_factory.db", check_same_thread=False)
cur = conn.cursor()

# إنشاء الجداول الأساسية
cur.execute("CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY, name TEXT, phone TEXT, address TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS suppliers (id INTEGER PRIMARY KEY, name TEXT, phone TEXT, item TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS inventory_in (id INTEGER PRIMARY KEY, date TEXT, supplier TEXT, item TEXT, qty REAL, price REAL, total REAL)")
cur.execute("CREATE TABLE IF NOT EXISTS sales (id INTEGER PRIMARY KEY, inv_no TEXT, date TEXT, customer TEXT, product TEXT, qty REAL, price REAL, total REAL, pay_type TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY, date TEXT, customer TEXT, amount REAL, notes TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS expenses (id INTEGER PRIMARY KEY, date TEXT, item TEXT, category TEXT, amount REAL, notes TEXT)")
conn.commit()

# عنوان التطبيق
st.title("🏭 نظام إدارة وحسابات مصنع نيبون")
st.markdown("---")

# القوائم والتبويبات
tab_dash, tab_sales, tab_inv, tab_exp, tab_setup = st.tabs([
    "📊 لوحة التحكم", 
    "💰 المبيعات والديون", 
    "📦 إدارة المخزن", 
    "📝 المصروفات", 
    "⚙️ البيانات الأساسية"
])

# 1. لوحة التحكم
with tab_dash:
    st.header("📊 الملخص المالي والأرباح")
    
    df_sales = pd.read_sql("SELECT SUM(total) as tot FROM sales", conn)
    total_sales = df_sales['tot'].iloc[0] or 0.0
    
    df_exp = pd.read_sql("SELECT SUM(amount) as tot FROM expenses", conn)
    total_exp = df_exp['tot'].iloc[0] or 0.0
    
    net_profit = total_sales - total_exp
    
    col1, col2, col3 = st.columns(3)
    col1.metric("إجمالي المبيعات", f"${total_sales:,.2f}")
    col2.metric("إجمالي المصروفات", f"${total_exp:,.2f}")
    col3.metric("صافي الأرباح", f"${net_profit:,.2f}")

# 2. المبيعات
with tab_sales:
    st.header("💰 سجل المبيعات والفواتير")
    with st.expander("➕ إضافة فاتورة جديدة"):
        inv_no = st.text_input("رقم الفاتورة")
        cust_list = [r[0] for r in cur.execute("SELECT name FROM customers").fetchall()]
        customer = st.selectbox("اسم العميل", cust_list if cust_list else [""])
        product = st.selectbox("المنتج", ["أكياس نفايات (حجم كبير)", "أكياس نفايات (حجم وسط)", "حبيبات بلاستيك"])
        qty = st.number_input("الكمية (طن)", min_value=0.0, step=0.1)
        price = st.number_input("سعر الطن ($)", min_value=0.0, step=10.0)
        pay_type = st.radio("نوع الدفع", ["آجل", "كاش"])
        
        if st.button("حفظ الفاتورة"):
            tot = qty * price
            date_str = datetime.now().strftime("%Y-%m-%d")
            cur.execute("INSERT INTO sales (inv_no, date, customer, product, qty, price, total, pay_type) VALUES (?,?,?,?,?,?,?,?)",
                        (inv_no, date_str, customer, product, qty, price, tot, pay_type))
            conn.commit()
            st.success("تم حفظ الفاتورة بنجاح!")
            st.rerun()

    st.subheader("سجل الفواتير المسجلة:")
    df_s = pd.read_sql("SELECT inv_no as 'رقم الفاتورة', date as 'التاريخ', customer as 'العميل', product as 'المنتج', qty as 'الكمية (طن)', price as 'السعر', total as 'الإجمالي', pay_type as 'نوع الدفع' FROM sales", conn)
    st.dataframe(df_s, use_container_width=True)

# 3. إدارة المخزن
with tab_inv:
    st.header("📦 إدارة المخزن والمشتريات")
    with st.expander("➕ إضافة مشتريات نيلون خام"):
        supp_list = [r[0] for r in cur.execute("SELECT name FROM suppliers").fetchall()]
        supp = st.selectbox("المورد", supp_list if supp_list else [""])
        qty_in = st.number_input("الكمية المشتراة (طن)", min_value=0.0, step=0.1)
        price_in = st.number_input("سعر شراء الطن ($)", min_value=0.0, step=10.0)
        
        if st.button("تسجيل المشتريات"):
            tot_in = qty_in * price_in
            date_str = datetime.now().strftime("%Y-%m-%d")
            cur.execute("INSERT INTO inventory_in (date, supplier, item, qty, price, total) VALUES (?,?,?,?,?,?)",
                        (date_str, supp, "نيلون خام", qty_in, price_in, tot_in))
            conn.commit()
            st.success("تم تسجيل المشتريات!")
            st.rerun()
            
    df_i = pd.read_sql("SELECT date as 'التاريخ', supplier as 'المورد', item as 'الصنف', qty as 'الكمية (طن)', price as 'سعر الطن', total as 'الإجمالي' FROM inventory_in", conn)
    st.dataframe(df_i, use_container_width=True)

# 4. المصروفات
with tab_exp:
    st.header("📝 المصروفات والرواتب")
    with st.expander("➕ تسجيل مصروف جديد"):
        item_exp = st.text_input("بند المصروف (مثلاً: كهرباء، رواتب)")
        cat_exp = st.selectbox("الفئة", ["مصاريف تشغيل", "أجور وراتب", "صيانة", "نقل"])
        amt_exp = st.number_input("المبلغ ($)", min_value=0.0, step=5.0)
        notes = st.text_input("ملاحظات")
        
        if st.button("حفظ المصروف"):
            date_str = datetime.now().strftime("%Y-%m-%d")
            cur.execute("INSERT INTO expenses (date, item, category, amount, notes) VALUES (?,?,?,?,?)",
                        (date_str, item_exp, cat_exp, amt_exp, notes))
            conn.commit()
            st.success("تم حفظ المصروف!")
            st.rerun()
            
    df_e = pd.read_sql("SELECT date as 'التاريخ', item as 'البند', category as 'الفئة', amount as 'المبلغ', notes as 'التفاصيل' FROM expenses", conn)
    st.dataframe(df_e, use_container_width=True)

# 5. البيانات الأساسية
with tab_setup:
    st.header("⚙️ إضافة عميل أو مورد جديد")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("إضافة عميل")
        c_name = st.text_input("اسم العميل")
        c_phone = st.text_input("رقم الهاتف")
        c_addr = st.text_input("العنوان")
        if st.button("إضافة العميل"):
            cur.execute("INSERT INTO customers (name, phone, address) VALUES (?,?,?)", (c_name, c_phone, c_addr))
            conn.commit()
            st.success("تمت إضافة العميل بنجاح!")
            st.rerun()
