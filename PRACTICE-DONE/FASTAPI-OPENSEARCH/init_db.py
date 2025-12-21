from database import Base, engine, SessionLocal, Product
import opensearch_client as os_client

def init():
    Base.metadata.create_all(bind=engine)
    os_client.create_index()
    
    db = SessionLocal()
    
    # Индексируем все товары в OpenSearch
    for product in db.query(Product).all():
        os_client.index_product(product)
    
    if db.query(Product).count() == 0:
        products = [
            Product(name="iPhone 15 Pro", description="Смартфон Apple с чипом A17 Pro, 256 ГБ", price=119990, category="Смартфоны", popularity=100),
            Product(name="Samsung Galaxy S24 Ultra", description="Флагманский смартфон Samsung с S Pen", price=109990, category="Смартфоны", popularity=95),
            Product(name="Xiaomi 14 Pro", description="Смартфон с камерой Leica, 512 ГБ", price=79990, category="Смартфоны", popularity=85),
            Product(name="HONOR Magic6 Pro", description="Смартфон с AI камерой", price=69990, category="Смартфоны", popularity=70),
            Product(name="MacBook Pro 14", description="Ноутбук Apple M3 Pro, 18 ГБ, 512 ГБ SSD", price=219990, category="Ноутбуки", popularity=90),
            Product(name="ASUS ROG Strix G16", description="Игровой ноутбук RTX 4060, 16 ГБ", price=129990, category="Ноутбуки", popularity=75),
            Product(name="Lenovo ThinkPad X1", description="Бизнес ноутбук Intel Core i7", price=159990, category="Ноутбуки", popularity=65),
            Product(name="AirPods Pro 2", description="Беспроводные наушники с шумоподавлением", price=24990, category="Наушники", popularity=95),
            Product(name="Sony WH-1000XM5", description="Накладные наушники с ANC", price=34990, category="Наушники", popularity=88),
            Product(name="JBL Tune 520BT", description="Беспроводные наушники", price=4990, category="Наушники", popularity=60),
            Product(name="iPad Air M2", description="Планшет Apple 11 дюймов, 128 ГБ", price=69990, category="Планшеты", popularity=80),
            Product(name="Samsung Galaxy Tab S9", description="Планшет Android с S Pen", price=59990, category="Планшеты", popularity=70),
            Product(name="Клавиатура Logitech MX Keys", description="Беспроводная клавиатура для Mac и Windows", price=12990, category="Аксессуары", popularity=75),
            Product(name="Мышь Logitech MX Master 3S", description="Беспроводная мышь для профессионалов", price=9990, category="Аксессуары", popularity=80),
            Product(name="Монитор LG UltraWide 34", description="Изогнутый монитор 3440x1440", price=49990, category="Мониторы", popularity=65),
            Product(name="Монитор Samsung Odyssey G7", description="Игровой монитор 240 Гц", price=54990, category="Мониторы", popularity=70),
            Product(name="Apple Watch Series 9", description="Умные часы с датчиком температуры", price=44990, category="Умные часы", popularity=90),
            Product(name="Samsung Galaxy Watch6", description="Умные часы на Wear OS", price=29990, category="Умные часы", popularity=75),
            Product(name="Яндекс Станция Макс", description="Умная колонка с Алисой", price=19990, category="Умный дом", popularity=85),
            Product(name="Xiaomi Robot Vacuum S10+", description="Робот-пылесос с самоочисткой", price=39990, category="Умный дом", popularity=70),
            Product(name="IOT", description="Умный дом", price=1000, category="Test", popularity=50),
            Product(name="Светильник ночной", description="Ночник Умник", price=1000, category="Test", popularity=50),
            Product(name="Test Product", description="Test Description", price=1000, category="Test", popularity=50),
            Product(name="Уборочный инвентарь", description="Швабра Умница", price=9999.99, category="Test Category", popularity=50),
            Product(name="Картина", description="Горе от ума", price=1000, category="Test", popularity=20),
        ]
        
        for product in products:
            db.add(product)
            db.commit()
            db.refresh(product)
            os_client.index_product(product)
    
    db.close()
    print("База данных инициализирована!")

if __name__ == "__main__":
    init()
