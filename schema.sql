CREATE TABLE
IF NOT EXISTS user_settings
(
"user_id" BIGINT,
"unique_id" VARCHAR,
"pref_repo" VARCHAR,
"pref_user" VARCHAR,
"pref_org" VARCHAR,
"personal_token" VARCHAR
);