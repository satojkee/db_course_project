-- Countries
INSERT INTO countries (name, minute_cost) VALUES
('CountryA', 0.5),
('CountryB', 0.7),
('CountryC', 1.0);

-- Cities
INSERT INTO cities (name, zip_code, country_id) VALUES
('City1', '11111', 1),
('City2', '22222', 1),
('City3', '33333', 2),
('City4', '44444', 2),
('City5', '55555', 3);

-- Rates
INSERT INTO rates (cost) VALUES
(250),
(450);

-- Categories
INSERT INTO categories (name, discount_mtp, rate_id) VALUES
('Standard', 1.0, 1),
('Premium', 0.8, 2),
('Business', 0.9, 1);

-- Customers
INSERT INTO customers (fullname, passport, city_id, category_id) VALUES
('Alice', 'A11111111', 1, 1),
('Bob', 'B22222222', 2, 2),
('Charlie', 'C33333333', 3, 1),
('Dana', 'D44444444', 4, 2),
('Eve', 'E55555555', 5, 3),
('Frank', 'F66666666', 1, 1),
('Grace', 'G77777777', 2, 2),
('Heidi', 'H88888888', 3, 3),
('Ivan', 'I99999999', 4, 1),
('Judy', 'J00000001', 5, 2),
('Karl', 'K00000002', 1, 3),
('Leo', 'L00000003', 2, 1),
('Mallory', 'M00000004', 3, 2),
('Niaj', 'N00000005', 4, 1),
('Olivia', 'O00000006', 5, 2),
('Peggy', 'P00000007', 1, 3),
('Quentin', 'Q00000008', 2, 1),
('Rupert', 'R00000009', 3, 2),
('Sybil', 'S00000010', 4, 3),
('Trent', 'T00000011', 5, 1);

-- Phone Numbers
INSERT INTO phone_numbers (number, customer_id) VALUES
('111-111',1),('222-222',2),('333-333',3),('444-444',4),('555-555',5),
('666-666',6),('777-777',7),('888-888',8),('999-999',9),('000-001',10),
('000-002',11),('000-003',12),('000-004',13),('000-005',14),('000-006',15),
('000-007',16),('000-008',17),('000-009',18),('000-010',19),('000-011',20);

-- Calls
INSERT INTO calls (from_customer_id, to_customer_id, duration, charge, started_at, finished_at, status) VALUES
(1,2,12,6.0,NOW() - INTERVAL '5 days', NOW() - INTERVAL '5 days','FINISHED'),
(2,3,25,12.5,NOW() - INTERVAL '10 days', NOW() - INTERVAL '10 days','FINISHED'),
(3,4,18,9.0,NOW() - INTERVAL '20 days', NOW() - INTERVAL '20 days','FINISHED'),
(4,5,35,17.5,NOW() - INTERVAL '25 days', NOW() - INTERVAL '25 days','FINISHED'),
(5,1,7,3.5,NOW() - INTERVAL '30 days', NOW() - INTERVAL '30 days','FINISHED'),
(6,7,50,20.0,NOW() - INTERVAL '40 days', NOW() - INTERVAL '40 days','FINISHED'),
(7,8,22,11.0,NOW() - INTERVAL '45 days', NOW() - INTERVAL '45 days','FINISHED'),
(8,9,15,7.5,NOW() - INTERVAL '50 days', NOW() - INTERVAL '50 days','FINISHED'),
(9,10,30,15.0,NOW() - INTERVAL '55 days', NOW() - INTERVAL '55 days','FINISHED'),
(10,1,10,5.0,NOW() - INTERVAL '60 days', NOW() - INTERVAL '60 days','FINISHED'),
(11,12,8,4.0,NOW() - INTERVAL '65 days', NOW() - INTERVAL '65 days','FINISHED'),
(12,13,45,18.0,NOW() - INTERVAL '70 days', NOW() - INTERVAL '70 days','FINISHED'),
(13,14,12,6.0,NOW() - INTERVAL '75 days', NOW() - INTERVAL '75 days','FINISHED'),
(14,15,20,10.0,NOW() - INTERVAL '80 days', NOW() - INTERVAL '80 days','FINISHED'),
(15,16,28,14.0,NOW() - INTERVAL '85 days', NOW() - INTERVAL '85 days','FINISHED'),
(16,17,32,16.0,NOW() - INTERVAL '90 days', NOW() - INTERVAL '90 days','FINISHED'),
(17,18,5,2.5,NOW() - INTERVAL '95 days', NOW() - INTERVAL '95 days','FINISHED'),
(18,19,38,19.0,NOW() - INTERVAL '100 days', NOW() - INTERVAL '100 days','FINISHED'),
(19,20,18,9.0,NOW() - INTERVAL '105 days', NOW() - INTERVAL '105 days','FINISHED'),
(20,1,25,12.5,NOW() - INTERVAL '110 days', NOW() - INTERVAL '110 days','FINISHED'),
(1,3,14,7.0,NOW() - INTERVAL '115 days', NOW() - INTERVAL '115 days','FINISHED'),
(2,4,19,9.5,NOW() - INTERVAL '120 days', NOW() - INTERVAL '120 days','FINISHED'),
(3,5,27,13.5,NOW() - INTERVAL '125 days', NOW() - INTERVAL '125 days','FINISHED'),
(4,6,22,11.0,NOW() - INTERVAL '130 days', NOW() - INTERVAL '130 days','FINISHED'),
(5,7,35,17.5,NOW() - INTERVAL '135 days', NOW() - INTERVAL '135 days','FINISHED'),
(6,8,10,5.0,NOW() - INTERVAL '140 days', NOW() - INTERVAL '140 days','FINISHED'),
(7,9,45,18.0,NOW() - INTERVAL '145 days', NOW() - INTERVAL '145 days','FINISHED'),
(8,10,20,10.0,NOW() - INTERVAL '150 days', NOW() - INTERVAL '150 days','FINISHED'),
(9,1,32,16.0,NOW() - INTERVAL '155 days', NOW() - INTERVAL '155 days','FINISHED'),
(10,2,28,14.0,NOW() - INTERVAL '160 days', NOW() - INTERVAL '160 days','FINISHED'),
(11,1,12,6.0,NOW() - INTERVAL '200 days', NOW() - INTERVAL '200 days','FINISHED'),
(12,2,18,9.0,NOW() - INTERVAL '205 days', NOW() - INTERVAL '205 days','FINISHED'),
(13,3,25,12.5,NOW() - INTERVAL '210 days', NOW() - INTERVAL '210 days','FINISHED'),
(14,4,30,15.0,NOW() - INTERVAL '215 days', NOW() - INTERVAL '215 days','FINISHED'),
(15,5,10,5.0,NOW() - INTERVAL '220 days', NOW() - INTERVAL '220 days','FINISHED'),
(16,6,15,7.5,NOW() - INTERVAL '225 days', NOW() - INTERVAL '225 days','FINISHED'),
(17,7,22,11.0,NOW() - INTERVAL '230 days', NOW() - INTERVAL '230 days','FINISHED'),
(18,8,18,9.0,NOW() - INTERVAL '235 days', NOW() - INTERVAL '235 days','FINISHED'),
(19,9,35,17.5,NOW() - INTERVAL '240 days', NOW() - INTERVAL '240 days','FINISHED'),
(20,10,40,20.0,NOW() - INTERVAL '245 days', NOW() - INTERVAL '245 days','FINISHED');

-- Admin user for application. Unhashed password: 11111111
INSERT INTO admins (username, password, created_at) VALUES
('admin', 'c4ffaab12d3e549b44da2eeff5ea213d10f6e6b4f0764621839a22e86874597c', NOW())