BEGIN;

INSERT INTO activity (id, created_at)
VALUES
    (1, now()),
    (2, now()),
    (3, now()),
    (4, now()),
    (5, now()),
    (6, now()),
    (7, now()),
    (8, now())
ON CONFLICT DO NOTHING;

INSERT INTO activity_name (id, activity_id, name, created_at)
VALUES
    (101, 1, 'Еда', now()),
    (102, 2, 'Мясная продукция', now()),
    (103, 3, 'Молочная продукция', now()),
    (104, 4, 'Автомобили', now()),
    (105, 5, 'Грузовые', now()),
    (106, 6, 'Легковые', now()),
    (107, 7, 'Запчасти', now()),
    (108, 8, 'Аксессуары', now())
ON CONFLICT DO NOTHING;

INSERT INTO activity_parent (id, activity_id, parent_id, created_at)
VALUES
    (201, 1, NULL, now()),
    (202, 2, 1, now()),
    (203, 3, 1, now()),
    (204, 4, NULL, now()),
    (205, 5, 4, now()),
    (206, 6, 4, now()),
    (207, 7, 6, now()),
    (208, 8, 6, now())
ON CONFLICT DO NOTHING;

INSERT INTO activity_closure (
    id,
    ancestor_id,
    descendant_id,
    depth,
    created_at
)
VALUES
    (301, 1, 1, 0, now()),
    (302, 2, 2, 0, now()),
    (303, 1, 2, 1, now()),
    (304, 3, 3, 0, now()),
    (305, 1, 3, 1, now()),
    (306, 4, 4, 0, now()),
    (307, 5, 5, 0, now()),
    (308, 4, 5, 1, now()),
    (309, 6, 6, 0, now()),
    (310, 4, 6, 1, now()),
    (311, 7, 7, 0, now()),
    (312, 6, 7, 1, now()),
    (313, 4, 7, 2, now()),
    (314, 8, 8, 0, now()),
    (315, 6, 8, 1, now()),
    (316, 4, 8, 2, now())
ON CONFLICT DO NOTHING;

INSERT INTO building (id, created_at)
VALUES
    (1, now()),
    (2, now())
ON CONFLICT DO NOTHING;

INSERT INTO building_address (id, building_id, address, created_at)
VALUES
    (401, 1, 'г. Москва, ул. Ленина 1, офис 3', now()),
    (402, 2, 'Блюхера, 32/1', now())
ON CONFLICT DO NOTHING;

INSERT INTO building_geo (id, building_id, geom, created_at)
VALUES
    (451, 1, ST_SetSRID(ST_Point(37.6173, 55.7558), 4326), now()),
    (452, 2, ST_SetSRID(ST_Point(82.9000, 55.0376), 4326), now())
ON CONFLICT DO NOTHING;

INSERT INTO agency (id, created_at)
VALUES
    (1, now()),
    (2, now()),
    (3, now())
ON CONFLICT DO NOTHING;

INSERT INTO agency_name (id, agency_id, name, created_at)
VALUES
    (501, 1, 'ООО "Рога и Копыта"', now()),
    (502, 2, 'ООО "АвтоТранс"', now()),
    (503, 3, 'ООО "Легковые Запчасти"', now())
ON CONFLICT DO NOTHING;

INSERT INTO agency_building (id, agency_id, building_id, created_at)
VALUES
    (551, 1, 2, now()),
    (552, 2, 1, now()),
    (553, 3, 1, now())
ON CONFLICT DO NOTHING;

INSERT INTO agency_phone (id, agency_id, phone, created_at)
VALUES
    (601, 1, '2-222-222', now()),
    (602, 1, '3-333-333', now()),
    (603, 1, '8-923-666-13-13', now()),
    (604, 2, '4-444-444', now()),
    (605, 3, '5-555-555', now())
ON CONFLICT DO NOTHING;

INSERT INTO agency_activity (id, agency_id, activity_id, created_at)
VALUES
    (701, 1, 2, now()),
    (702, 1, 3, now()),
    (703, 2, 5, now()),
    (704, 3, 7, now()),
    (705, 3, 8, now())
ON CONFLICT DO NOTHING;

COMMIT;
