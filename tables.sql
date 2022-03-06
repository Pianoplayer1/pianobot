CREATE TABLE "guildActivity" (
    "time" timestamp(0) without time zone NOT NULL,
    "Eden" integer,
    "ShadowFall" integer,
    "Avicia" integer,
    "IceBlue Team" integer,
    "Guardian of Wynn" integer,
    "The Mage Legacy" integer,
    "Emorians" integer,
    "Paladins United" integer,
    "Lux Nova" integer,
    "HackForums" integer,
    "The Aquarium" integer,
    "The Simple Ones" integer,
    "Empire of Sindria" integer,
    "Titans Valor" integer,
    "The Dark Phoenix" integer,
    "Nethers Ascent" integer,
    "Sins of Seedia" integer,
    "WrathOfTheFallen" integer,
    "busted moments" integer,
    "Nefarious Ravens" integer,
    "Aequitas" integer,
    "Nerfuria" integer,
    "KongoBoys" integer,
    "Forever Twilight" integer,
    "Gabameno" integer,
    "LittleBunny Land" integer,
    "Kingdom Foxes" integer,
    "Jeus" integer,
    "TheNoLifes" integer,
    "Cyphrus Code" integer,
    "Profession Heaven" integer,
    "Idiot Co" integer,
    "SICA Team" integer,
    "Achte Shadow" integer,
    "Skuc Nation" integer,
    "Fuzzy Spiders" integer,
    "Syndicate of Nyx" integer,
    "TVietNam" integer,
    "ForsakenLaws" integer,
    "Last Order" integer,
    "The Broken Gasmask" integer,
    "Breadskate" integer,
    "Atlas Inc" integer,
    "Question Mark Syndicate" integer,
    "Blacklisted" integer,
    "Tartarus Wrath" integer,
    "Opus Maximus" integer,
    "TruthSworD" integer,
    "Jasmine Dragon" integer,
    "Gopniks" integer,
    "Crystal Iris" integer,
    "Wheres The Finish" integer,
    "Germany" integer,
    "FlameKnights" integer,
    "WynnFairyTail" integer,
    "Gang of Fools" integer DEFAULT 0
);


CREATE TABLE "guildXP" (
    "time" timestamp without time zone NOT NULL
);


CREATE TABLE guilds (
    name character varying(30) NOT NULL,
    tag character varying(4) NOT NULL,
    level integer NOT NULL,
    xp bigint NOT NULL,
    territories integer NOT NULL,
    warcount integer NOT NULL,
    members integer NOT NULL,
    created timestamp with time zone NOT NULL
);


CREATE TABLE member_activity (
    username character varying(16) NOT NULL
);


CREATE TABLE members (
    uuid character varying(36) NOT NULL,
    name character varying(16) NOT NULL,
    discord bigint NOT NULL,
    rank character varying NOT NULL,
    joined bigint NOT NULL,
    last_seen bigint NOT NULL,
    online bigint NOT NULL,
    xp bigint NOT NULL
);


CREATE TABLE servers (
    id bigint NOT NULL,
    prefix character varying(3) DEFAULT '-'::character varying NOT NULL,
    channel bigint DEFAULT '0'::bigint NOT NULL,
    role bigint DEFAULT '0'::bigint NOT NULL,
    "time" integer,
    ping integer DEFAULT 1800 NOT NULL,
    rank integer DEFAULT '-1'::integer
);


CREATE TABLE territories (
    name character varying(50) NOT NULL,
    guild character varying(30) NOT NULL
);


CREATE TABLE worlds (
    world character varying(4) NOT NULL,
    "time" integer NOT NULL
);


ALTER TABLE ONLY "guildActivity"
    ADD CONSTRAINT "guildActivity_pkey" PRIMARY KEY ("time");


ALTER TABLE ONLY "guildXP"
    ADD CONSTRAINT "guildXP_pkey" PRIMARY KEY ("time");


ALTER TABLE ONLY guilds
    ADD CONSTRAINT guilds_pkey PRIMARY KEY (tag);


ALTER TABLE ONLY member_activity
    ADD CONSTRAINT member_activity_pkey PRIMARY KEY (username);


ALTER TABLE ONLY members
    ADD CONSTRAINT members_pkey PRIMARY KEY (uuid);


LTER TABLE ONLY servers
    ADD CONSTRAINT servers_pkey PRIMARY KEY (id);


ALTER TABLE ONLY territories
    ADD CONSTRAINT territories_pkey PRIMARY KEY (name);


ALTER TABLE ONLY worlds
    ADD CONSTRAINT worlds_pkey PRIMARY KEY (world);