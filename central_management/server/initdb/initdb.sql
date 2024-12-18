CREATE TABLE ev_user (
  user_id varchar(128) NOT NULL PRIMARY KEY
);

CREATE TABLE cardinfo (
  cardnum varchar(16) NOT NULL,
  user_id varchar(128) NOT NULL,
  CONSTRAINT card_info_ibfk_1 FOREIGN KEY (user_id) REFERENCES ev_user(user_id)
);

CREATE TABLE charging_station (
  id varchar(16) NOT NULL PRIMARY KEY
); 

CREATE TABLE charging_session (
  session_id SERIAL PRIMARY KEY,
  charging_station_id VARCHAR(16) NOT NULL,
  user_id VARCHAR(128) NOT NULL,
  start_time TIMESTAMP, 
  stop_time TIMESTAMP,
  price FLOAT, 
  energy FLOAT,
  tariff FLOAT,
  CONSTRAINT charging_session_ibfk_1 FOREIGN KEY (charging_station_id) REFERENCES charging_station(id),
  CONSTRAINT charging_session_ibfk_2 FOREIGN KEY (user_id) REFERENCES ev_user(user_id)
);

INSERT INTO ev_user (user_id) VALUES 
  ('user1'),
  ('user2');

INSERT INTO charging_station (id) VALUES 
  ('CP_1'); 