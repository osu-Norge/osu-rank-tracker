-- The schema as it was when migrations were introduced. IF NOT EXISTS leaves existing databases alone

CREATE TABLE IF NOT EXISTS public.guild (
    discord_id bigint NOT NULL PRIMARY KEY,
    whitelisted_countries char(2)[],
    blacklisted_osu_users integer[],
    role_remove bigint,
    role_add bigint,
    role_1_digit bigint,
    role_2_digit bigint,
    role_3_digit bigint,
    role_4_digit bigint,
    role_5_digit bigint,
    role_6_digit bigint,
    role_7_digit bigint,
    role_standard bigint,
    role_taiko bigint,
    role_ctb bigint,
    role_mania bigint
);

CREATE TABLE IF NOT EXISTS public.user (
    discord_id bigint NOT NULL PRIMARY KEY,
    osu_id integer NOT NULL,
    gamemode smallint NOT NULL
);

CREATE TABLE IF NOT EXISTS public.verification (
    discord_id bigint NOT NULL PRIMARY KEY,
    uuid TEXT NOT NULL,
    expires TIMESTAMP
);
