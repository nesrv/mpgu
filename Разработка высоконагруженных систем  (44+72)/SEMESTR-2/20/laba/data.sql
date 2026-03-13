-- Наполнение для e-shop: каталог, корзины, заказы (для HTMX-страниц и Debug Toolbar / Silk).
-- Видеокарты (id 1..5 в порядке вставки). Нужны миграции shop до Cart/Order/OrderItem.
INSERT INTO video_cards (name, price, description, created_at) VALUES
  ('NVIDIA GeForce RTX 5090', 230000.00, 'Флагманская видеокарта 2026 года.', '2026-01-15 10:00:00'),
  ('NVIDIA GeForce RTX 4090', 165000.00, 'Мощная видеокарта для рейтрейсинга.', '2026-01-15 10:00:00'),
  ('NVIDIA GeForce RTX 5080', 130000.00, 'Высокая производительность для 4K.', '2026-01-15 10:00:00'),
  ('AMD Radeon RX 9070 XT', 95000.00, 'Лучшее соотношение цена/производительность.', '2026-01-15 10:00:00'),
  ('NVIDIA GeForce RTX 4080 Super', 115000.00, 'Мощная видеокарта для 4K с DLSS.', '2026-01-15 10:00:00');

-- Корзины (shop_cart): product_id → video_cards.id
INSERT INTO shop_cart (product_id, qty, created_at) VALUES
  (1, 1, '2026-02-01 09:15:00'),
  (3, 2, '2026-02-01 11:30:00'),
  (4, 1, '2026-02-02 14:00:00'),
  (2, 1, '2026-02-03 16:45:00'),
  (5, 3, '2026-02-04 10:20:00'),
  (1, 2, '2026-02-05 08:00:00'),
  (4, 2, '2026-02-06 19:10:00');

-- Заказы (shop_order)
INSERT INTO shop_order (total, created_at) VALUES
  (395000.00, '2026-02-10 12:00:00'),
  (320000.00, '2026-02-11 15:30:00'),
  (115000.00, '2026-02-12 09:00:00'),
  (460000.00, '2026-02-13 18:20:00'),
  (95000.00,  '2026-02-14 11:45:00');

-- Позиции заказов (shop_orderitem); order_id 1..5 в порядке вставки заказов
INSERT INTO shop_orderitem (order_id, product_name, qty, price) VALUES
  (1, 'NVIDIA GeForce RTX 5090', 1, 230000.00),
  (1, 'NVIDIA GeForce RTX 4090', 1, 165000.00),
  (2, 'AMD Radeon RX 9070 XT', 2, 95000.00),
  (2, 'NVIDIA GeForce RTX 5080', 1, 130000.00),
  (3, 'NVIDIA GeForce RTX 4080 Super', 1, 115000.00),
  (4, 'NVIDIA GeForce RTX 5090', 2, 230000.00),
  (5, 'AMD Radeon RX 9070 XT', 1, 95000.00);

-- PostgreSQL: подогнать serial после ручных вставок (по желанию)
-- SELECT setval(pg_get_serial_sequence('shop_cart','id'), (SELECT COALESCE(MAX(id),1) FROM shop_cart));
-- SELECT setval(pg_get_serial_sequence('shop_order','id'), (SELECT COALESCE(MAX(id),1) FROM shop_order));
-- SELECT setval(pg_get_serial_sequence('shop_orderitem','id'), (SELECT COALESCE(MAX(id),1) FROM shop_orderitem));