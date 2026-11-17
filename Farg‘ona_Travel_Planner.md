# Farg‘ona Travel Planner

Farg‘ona viloyatidagi turistik obyektlar asosida foydalanuvchining qiziqishi, vaqti va byudjetiga mos marshrut tavsiya qiluvchi Streamlit ilova.

## Ishga tushirish

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Ilova brauzerda `http://localhost:8501` manzilida ochiladi.

## Imkoniyatlar

- Qiziqish turlarini tanlash
- Maksimal byudjet va safar davomiyligini belgilash
- Hudud bo‘yicha filtr
- Tavsiya etilgan marshrutni kartochkalar va jadval ko‘rinishida ko‘rish
- Vaqt taqsimotini grafikda ko‘rish
- Marshrutni CSV formatida yuklab olish
