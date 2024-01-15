CREATE TABLE IF NOT EXISTS blacklist (
  id SERIAL PRIMARY KEY,
  user_id varchar(20) NOT NULL,
  created_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS context_message (
  id SERIAL PRIMARY KEY,
  message_id varchar(20) NOT NULL UNIQUE,
  added_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  added_by varchar(20) NOT NULL,
  times_played INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS nword_counter (
  id SERIAL PRIMARY KEY,
  user_id varchar(20) NOT NULL UNIQUE,
  count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS command_stats (
  id SERIAL PRIMARY KEY,
  command varchar(20) NOT NULL,
  user_id varchar(20) NOT NULL,
  count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS user_bans (
  id SERIAL PRIMARY KEY,
  user_id varchar(20) NOT NULL UNIQUE,
  count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS reminders (
  id SERIAL PRIMARY KEY,
  user_id varchar(20) NOT NULL,
  subject varchar(100) NOT NULL,
  time varchar(25) NOT NULL
);

CREATE TABLE IF NOT EXISTS polls (
  id SERIAL PRIMARY KEY,
  message_id varchar(20) NOT NULL,
  reactions varchar(20)[][]
);

CREATE TABLE IF NOT EXISTS nicknames (
  id SERIAL PRIMARY KEY,
  server_id varchar(20) NOT NULL DEFAULT '710963677943169107',
  user_id varchar(20) NOT NULL,
  nickname varchar(32) NOT NULL
);

CREATE TABLE IF NOT EXISTS autoroles (
  id SERIAL PRIMARY KEY,
  server_id varchar(20) NOT NULL DEFAULT '710963677943169107',
  user_id varchar(20) NOT NULL,
  roles varchar(20)[]
);

CREATE TABLE IF NOT EXISTS poses (
  id SERIAL PRIMARY KEY,
  user_id varchar(20) NOT NULL,
  active_poses INTEGER[],
  place INTEGER NOT NULL
);