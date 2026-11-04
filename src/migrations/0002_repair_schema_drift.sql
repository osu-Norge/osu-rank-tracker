-- Older schema changes were only made to the CREATE TABLE statements, so databases created before them still
-- have the old schema. Every statement here does nothing on a database that's already up to date

-- Until 2023-02-26 guilds had a registration channel, stored in a channel table, and a moderator role
ALTER TABLE public.guild DROP COLUMN IF EXISTS registration_channel;
ALTER TABLE public.guild DROP COLUMN IF EXISTS role_moderator;
DROP TABLE IF EXISTS public.channel;

-- Until 2025-01-14 pending verifications had no expiry
ALTER TABLE public.verification ADD COLUMN IF NOT EXISTS expires TIMESTAMP;

-- The very first schema (2022-12-20) used integer Discord IDs, which are too small for them, allowed users
-- without an osu! ID or gamemode and had no primary key for verifications
ALTER TABLE public.user ALTER COLUMN discord_id TYPE bigint;
ALTER TABLE public.user ALTER COLUMN osu_id SET NOT NULL;
ALTER TABLE public.user ALTER COLUMN gamemode SET NOT NULL;
ALTER TABLE public.verification ALTER COLUMN discord_id TYPE bigint;
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_constraint WHERE conrelid = 'public.verification'::regclass AND contype = 'p') THEN
        ALTER TABLE public.verification ADD PRIMARY KEY (discord_id);
    END IF;
END
$$;
