-- Seed regions manually

INSERT INTO region (region_name) VALUES
('North Scotland'),
('South Scotland'),
('North West England'),
('North East England'),
('Yorkshire'),
('North Wales & Merseyside'),
('South Wales'),
('West Midlands'),
('East Midlands'),
('East England'),
('South West England'),
('South England'),
('London'),
('South East England'),
('England'),
('Scotland'),
('Wales'),
('GB');


-- Seed categories manually
INSERT INTO category (category_id, category) VALUES
    (1,  'HV ISOLATION'),
    (2,  'LV GENERIC'),
    (3,  'LV OVERHEAD'),
    (4,  'LV UNDERGROUND'),
    (5,  'HV OVERHEAD'),
    (6,  'LV ISOLATION'),
    (7,  'LV FUSE'),
    (8,  'HV GENERIC'),
    (9,  'HV DAMAGE'),
    (10, 'LV DAMAGE'),
    (11, 'HV FUSE'),
    (12, 'HV UNDERGROUND'),
    (13, 'EHV OVERHEAD'),
    (14, 'HV PLANT')
ON CONFLICT (category_id) DO NOTHING;
