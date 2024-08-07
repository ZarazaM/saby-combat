PGDMP     %                    |            saby_combat    13.6    13.6 R    w           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false            x           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            y           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            z           1262    54741    saby_combat    DATABASE     o   CREATE DATABASE saby_combat WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE = 'English_United States.1252';
    DROP DATABASE saby_combat;
                postgres    false                        3079    35226    citext 	   EXTENSION     :   CREATE EXTENSION IF NOT EXISTS citext WITH SCHEMA public;
    DROP EXTENSION citext;
                   false            {           0    0    EXTENSION citext    COMMENT     S   COMMENT ON EXTENSION citext IS 'data type for case-insensitive character strings';
                        false    2            �            1259    54742    alembic_version    TABLE     X   CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);
 #   DROP TABLE public.alembic_version;
       public         heap    saby_combat_dev    false            �            1259    54853    clan_invitations    TABLE     �   CREATE TABLE public.clan_invitations (
    invitation_id integer NOT NULL,
    user_id integer,
    clan_id integer,
    sender_id integer,
    status character varying(20)
);
 $   DROP TABLE public.clan_invitations;
       public         heap    saby_combat_dev    false            �            1259    54851 "   clan_invitations_invitation_id_seq    SEQUENCE     �   CREATE SEQUENCE public.clan_invitations_invitation_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 9   DROP SEQUENCE public.clan_invitations_invitation_id_seq;
       public          saby_combat_dev    false    219            |           0    0 "   clan_invitations_invitation_id_seq    SEQUENCE OWNED BY     i   ALTER SEQUENCE public.clan_invitations_invitation_id_seq OWNED BY public.clan_invitations.invitation_id;
          public          saby_combat_dev    false    218            �            1259    54799    clans    TABLE     �   CREATE TABLE public.clans (
    id integer NOT NULL,
    clan_name character varying(100) NOT NULL,
    leader_id integer,
    is_open boolean
);
    DROP TABLE public.clans;
       public         heap    saby_combat_dev    false            �            1259    54797    clans_id_seq    SEQUENCE     �   CREATE SEQUENCE public.clans_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 #   DROP SEQUENCE public.clans_id_seq;
       public          saby_combat_dev    false    213            }           0    0    clans_id_seq    SEQUENCE OWNED BY     =   ALTER SEQUENCE public.clans_id_seq OWNED BY public.clans.id;
          public          saby_combat_dev    false    212            �            1259    54812    friends    TABLE     L   CREATE TABLE public.friends (
    user_id integer,
    friend_id integer
);
    DROP TABLE public.friends;
       public         heap    saby_combat_dev    false            �            1259    54749    levels    TABLE     �   CREATE TABLE public.levels (
    id integer NOT NULL,
    level_name character varying(50) NOT NULL,
    coins_required bigint NOT NULL,
    coins_per_click integer NOT NULL
);
    DROP TABLE public.levels;
       public         heap    saby_combat_dev    false            �            1259    54747    levels_id_seq    SEQUENCE     �   CREATE SEQUENCE public.levels_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 $   DROP SEQUENCE public.levels_id_seq;
       public          saby_combat_dev    false    203            ~           0    0    levels_id_seq    SEQUENCE OWNED BY     ?   ALTER SEQUENCE public.levels_id_seq OWNED BY public.levels.id;
          public          saby_combat_dev    false    202            �            1259    54757    upgrades    TABLE       CREATE TABLE public.upgrades (
    id integer NOT NULL,
    upgrade_name character varying(100) NOT NULL,
    upgrade_image character varying(255),
    base_cost bigint NOT NULL,
    coins_per_second bigint NOT NULL,
    cost_multiplier integer NOT NULL
);
    DROP TABLE public.upgrades;
       public         heap    saby_combat_dev    false            �            1259    54755    upgrades_id_seq    SEQUENCE     �   CREATE SEQUENCE public.upgrades_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 &   DROP SEQUENCE public.upgrades_id_seq;
       public          saby_combat_dev    false    205                       0    0    upgrades_id_seq    SEQUENCE OWNED BY     C   ALTER SEQUENCE public.upgrades_id_seq OWNED BY public.upgrades.id;
          public          saby_combat_dev    false    204            �            1259    54827 
   user_coins    TABLE     �   CREATE TABLE public.user_coins (
    user_id integer NOT NULL,
    total_coins bigint,
    current_coins bigint,
    click_count integer,
    coins_per_second bigint,
    level_id integer
);
    DROP TABLE public.user_coins;
       public         heap    saby_combat_dev    false            �            1259    54825    user_coins_user_id_seq    SEQUENCE     �   CREATE SEQUENCE public.user_coins_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 -   DROP SEQUENCE public.user_coins_user_id_seq;
       public          saby_combat_dev    false    216            �           0    0    user_coins_user_id_seq    SEQUENCE OWNED BY     Q   ALTER SEQUENCE public.user_coins_user_id_seq OWNED BY public.user_coins.user_id;
          public          saby_combat_dev    false    215            �            1259    54767 	   user_info    TABLE       CREATE TABLE public.user_info (
    user_id integer NOT NULL,
    status character varying(30),
    description_profile character varying(120),
    profile_picture character varying(255),
    age smallint,
    city character varying(30),
    gender smallint
);
    DROP TABLE public.user_info;
       public         heap    saby_combat_dev    false            �            1259    54765    user_info_user_id_seq    SEQUENCE     �   CREATE SEQUENCE public.user_info_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 ,   DROP SEQUENCE public.user_info_user_id_seq;
       public          saby_combat_dev    false    207            �           0    0    user_info_user_id_seq    SEQUENCE OWNED BY     O   ALTER SEQUENCE public.user_info_user_id_seq OWNED BY public.user_info.user_id;
          public          saby_combat_dev    false    206            �            1259    54838    user_upgrades    TABLE     i   CREATE TABLE public.user_upgrades (
    user_id integer,
    upgrade_id integer,
    quantity integer
);
 !   DROP TABLE public.user_upgrades;
       public         heap    saby_combat_dev    false            �            1259    54775    user_verification    TABLE     �   CREATE TABLE public.user_verification (
    user_id integer NOT NULL,
    email_verified boolean,
    verified_on timestamp without time zone
);
 %   DROP TABLE public.user_verification;
       public         heap    saby_combat_dev    false            �            1259    54773    user_verification_user_id_seq    SEQUENCE     �   CREATE SEQUENCE public.user_verification_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 4   DROP SEQUENCE public.user_verification_user_id_seq;
       public          saby_combat_dev    false    209            �           0    0    user_verification_user_id_seq    SEQUENCE OWNED BY     _   ALTER SEQUENCE public.user_verification_user_id_seq OWNED BY public.user_verification.user_id;
          public          saby_combat_dev    false    208            �            1259    54783    users    TABLE     �  CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(50) NOT NULL,
    name character varying(30) NOT NULL,
    surname character varying(30) NOT NULL,
    patronymic character varying(30),
    email character varying(100) NOT NULL,
    password_hash character varying(255) NOT NULL,
    role boolean,
    created_at timestamp without time zone DEFAULT now(),
    blocked boolean,
    clan_id integer,
    referral_link character varying(40) NOT NULL
);
    DROP TABLE public.users;
       public         heap    saby_combat_dev    false            �            1259    54781    users_id_seq    SEQUENCE     �   CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 #   DROP SEQUENCE public.users_id_seq;
       public          saby_combat_dev    false    211            �           0    0    users_id_seq    SEQUENCE OWNED BY     =   ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;
          public          saby_combat_dev    false    210            �           2604    54856    clan_invitations invitation_id    DEFAULT     �   ALTER TABLE ONLY public.clan_invitations ALTER COLUMN invitation_id SET DEFAULT nextval('public.clan_invitations_invitation_id_seq'::regclass);
 M   ALTER TABLE public.clan_invitations ALTER COLUMN invitation_id DROP DEFAULT;
       public          saby_combat_dev    false    219    218    219            �           2604    54802    clans id    DEFAULT     d   ALTER TABLE ONLY public.clans ALTER COLUMN id SET DEFAULT nextval('public.clans_id_seq'::regclass);
 7   ALTER TABLE public.clans ALTER COLUMN id DROP DEFAULT;
       public          saby_combat_dev    false    213    212    213            �           2604    54752 	   levels id    DEFAULT     f   ALTER TABLE ONLY public.levels ALTER COLUMN id SET DEFAULT nextval('public.levels_id_seq'::regclass);
 8   ALTER TABLE public.levels ALTER COLUMN id DROP DEFAULT;
       public          saby_combat_dev    false    202    203    203            �           2604    54760    upgrades id    DEFAULT     j   ALTER TABLE ONLY public.upgrades ALTER COLUMN id SET DEFAULT nextval('public.upgrades_id_seq'::regclass);
 :   ALTER TABLE public.upgrades ALTER COLUMN id DROP DEFAULT;
       public          saby_combat_dev    false    204    205    205            �           2604    54830    user_coins user_id    DEFAULT     x   ALTER TABLE ONLY public.user_coins ALTER COLUMN user_id SET DEFAULT nextval('public.user_coins_user_id_seq'::regclass);
 A   ALTER TABLE public.user_coins ALTER COLUMN user_id DROP DEFAULT;
       public          saby_combat_dev    false    216    215    216            �           2604    54770    user_info user_id    DEFAULT     v   ALTER TABLE ONLY public.user_info ALTER COLUMN user_id SET DEFAULT nextval('public.user_info_user_id_seq'::regclass);
 @   ALTER TABLE public.user_info ALTER COLUMN user_id DROP DEFAULT;
       public          saby_combat_dev    false    207    206    207            �           2604    54778    user_verification user_id    DEFAULT     �   ALTER TABLE ONLY public.user_verification ALTER COLUMN user_id SET DEFAULT nextval('public.user_verification_user_id_seq'::regclass);
 H   ALTER TABLE public.user_verification ALTER COLUMN user_id DROP DEFAULT;
       public          saby_combat_dev    false    208    209    209            �           2604    54786    users id    DEFAULT     d   ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);
 7   ALTER TABLE public.users ALTER COLUMN id DROP DEFAULT;
       public          saby_combat_dev    false    210    211    211            b          0    54742    alembic_version 
   TABLE DATA           6   COPY public.alembic_version (version_num) FROM stdin;
    public          saby_combat_dev    false    201   �b       t          0    54853    clan_invitations 
   TABLE DATA           ^   COPY public.clan_invitations (invitation_id, user_id, clan_id, sender_id, status) FROM stdin;
    public          saby_combat_dev    false    219   �b       n          0    54799    clans 
   TABLE DATA           B   COPY public.clans (id, clan_name, leader_id, is_open) FROM stdin;
    public          saby_combat_dev    false    213   �b       o          0    54812    friends 
   TABLE DATA           5   COPY public.friends (user_id, friend_id) FROM stdin;
    public          saby_combat_dev    false    214   �b       d          0    54749    levels 
   TABLE DATA           Q   COPY public.levels (id, level_name, coins_required, coins_per_click) FROM stdin;
    public          saby_combat_dev    false    203   c       f          0    54757    upgrades 
   TABLE DATA           q   COPY public.upgrades (id, upgrade_name, upgrade_image, base_cost, coins_per_second, cost_multiplier) FROM stdin;
    public          saby_combat_dev    false    205   7c       q          0    54827 
   user_coins 
   TABLE DATA           r   COPY public.user_coins (user_id, total_coins, current_coins, click_count, coins_per_second, level_id) FROM stdin;
    public          saby_combat_dev    false    216   Tc       h          0    54767 	   user_info 
   TABLE DATA           m   COPY public.user_info (user_id, status, description_profile, profile_picture, age, city, gender) FROM stdin;
    public          saby_combat_dev    false    207   qc       r          0    54838    user_upgrades 
   TABLE DATA           F   COPY public.user_upgrades (user_id, upgrade_id, quantity) FROM stdin;
    public          saby_combat_dev    false    217   �c       j          0    54775    user_verification 
   TABLE DATA           Q   COPY public.user_verification (user_id, email_verified, verified_on) FROM stdin;
    public          saby_combat_dev    false    209   �c       l          0    54783    users 
   TABLE DATA           �   COPY public.users (id, username, name, surname, patronymic, email, password_hash, role, created_at, blocked, clan_id, referral_link) FROM stdin;
    public          saby_combat_dev    false    211   �c       �           0    0 "   clan_invitations_invitation_id_seq    SEQUENCE SET     Q   SELECT pg_catalog.setval('public.clan_invitations_invitation_id_seq', 1, false);
          public          saby_combat_dev    false    218            �           0    0    clans_id_seq    SEQUENCE SET     ;   SELECT pg_catalog.setval('public.clans_id_seq', 1, false);
          public          saby_combat_dev    false    212            �           0    0    levels_id_seq    SEQUENCE SET     <   SELECT pg_catalog.setval('public.levels_id_seq', 1, false);
          public          saby_combat_dev    false    202            �           0    0    upgrades_id_seq    SEQUENCE SET     >   SELECT pg_catalog.setval('public.upgrades_id_seq', 1, false);
          public          saby_combat_dev    false    204            �           0    0    user_coins_user_id_seq    SEQUENCE SET     E   SELECT pg_catalog.setval('public.user_coins_user_id_seq', 1, false);
          public          saby_combat_dev    false    215            �           0    0    user_info_user_id_seq    SEQUENCE SET     D   SELECT pg_catalog.setval('public.user_info_user_id_seq', 1, false);
          public          saby_combat_dev    false    206            �           0    0    user_verification_user_id_seq    SEQUENCE SET     L   SELECT pg_catalog.setval('public.user_verification_user_id_seq', 1, false);
          public          saby_combat_dev    false    208            �           0    0    users_id_seq    SEQUENCE SET     ;   SELECT pg_catalog.setval('public.users_id_seq', 1, false);
          public          saby_combat_dev    false    210            �           2606    54746 #   alembic_version alembic_version_pkc 
   CONSTRAINT     j   ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);
 M   ALTER TABLE ONLY public.alembic_version DROP CONSTRAINT alembic_version_pkc;
       public            saby_combat_dev    false    201            �           2606    54858 &   clan_invitations clan_invitations_pkey 
   CONSTRAINT     o   ALTER TABLE ONLY public.clan_invitations
    ADD CONSTRAINT clan_invitations_pkey PRIMARY KEY (invitation_id);
 P   ALTER TABLE ONLY public.clan_invitations DROP CONSTRAINT clan_invitations_pkey;
       public            saby_combat_dev    false    219            �           2606    54806    clans clans_clan_name_key 
   CONSTRAINT     Y   ALTER TABLE ONLY public.clans
    ADD CONSTRAINT clans_clan_name_key UNIQUE (clan_name);
 C   ALTER TABLE ONLY public.clans DROP CONSTRAINT clans_clan_name_key;
       public            saby_combat_dev    false    213            �           2606    54804    clans clans_pkey 
   CONSTRAINT     N   ALTER TABLE ONLY public.clans
    ADD CONSTRAINT clans_pkey PRIMARY KEY (id);
 :   ALTER TABLE ONLY public.clans DROP CONSTRAINT clans_pkey;
       public            saby_combat_dev    false    213            �           2606    54754    levels levels_pkey 
   CONSTRAINT     P   ALTER TABLE ONLY public.levels
    ADD CONSTRAINT levels_pkey PRIMARY KEY (id);
 <   ALTER TABLE ONLY public.levels DROP CONSTRAINT levels_pkey;
       public            saby_combat_dev    false    203            �           2606    54762    upgrades upgrades_pkey 
   CONSTRAINT     T   ALTER TABLE ONLY public.upgrades
    ADD CONSTRAINT upgrades_pkey PRIMARY KEY (id);
 @   ALTER TABLE ONLY public.upgrades DROP CONSTRAINT upgrades_pkey;
       public            saby_combat_dev    false    205            �           2606    54764 "   upgrades upgrades_upgrade_name_key 
   CONSTRAINT     e   ALTER TABLE ONLY public.upgrades
    ADD CONSTRAINT upgrades_upgrade_name_key UNIQUE (upgrade_name);
 L   ALTER TABLE ONLY public.upgrades DROP CONSTRAINT upgrades_upgrade_name_key;
       public            saby_combat_dev    false    205            �           2606    54832    user_coins user_coins_pkey 
   CONSTRAINT     ]   ALTER TABLE ONLY public.user_coins
    ADD CONSTRAINT user_coins_pkey PRIMARY KEY (user_id);
 D   ALTER TABLE ONLY public.user_coins DROP CONSTRAINT user_coins_pkey;
       public            saby_combat_dev    false    216            �           2606    54772    user_info user_info_pkey 
   CONSTRAINT     [   ALTER TABLE ONLY public.user_info
    ADD CONSTRAINT user_info_pkey PRIMARY KEY (user_id);
 B   ALTER TABLE ONLY public.user_info DROP CONSTRAINT user_info_pkey;
       public            saby_combat_dev    false    207            �           2606    54780 (   user_verification user_verification_pkey 
   CONSTRAINT     k   ALTER TABLE ONLY public.user_verification
    ADD CONSTRAINT user_verification_pkey PRIMARY KEY (user_id);
 R   ALTER TABLE ONLY public.user_verification DROP CONSTRAINT user_verification_pkey;
       public            saby_combat_dev    false    209            �           2606    54794    users users_email_key 
   CONSTRAINT     Q   ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);
 ?   ALTER TABLE ONLY public.users DROP CONSTRAINT users_email_key;
       public            saby_combat_dev    false    211            �           2606    54792    users users_pkey 
   CONSTRAINT     N   ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);
 :   ALTER TABLE ONLY public.users DROP CONSTRAINT users_pkey;
       public            saby_combat_dev    false    211            �           2606    54796    users users_username_key 
   CONSTRAINT     W   ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);
 B   ALTER TABLE ONLY public.users DROP CONSTRAINT users_username_key;
       public            saby_combat_dev    false    211            �           2606    54859 .   clan_invitations clan_invitations_clan_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.clan_invitations
    ADD CONSTRAINT clan_invitations_clan_id_fkey FOREIGN KEY (clan_id) REFERENCES public.clans(id) ON DELETE CASCADE;
 X   ALTER TABLE ONLY public.clan_invitations DROP CONSTRAINT clan_invitations_clan_id_fkey;
       public          saby_combat_dev    false    213    3026    219            �           2606    54864 0   clan_invitations clan_invitations_sender_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.clan_invitations
    ADD CONSTRAINT clan_invitations_sender_id_fkey FOREIGN KEY (sender_id) REFERENCES public.users(id) ON DELETE CASCADE;
 Z   ALTER TABLE ONLY public.clan_invitations DROP CONSTRAINT clan_invitations_sender_id_fkey;
       public          saby_combat_dev    false    219    211    3020            �           2606    54869 .   clan_invitations clan_invitations_user_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.clan_invitations
    ADD CONSTRAINT clan_invitations_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;
 X   ALTER TABLE ONLY public.clan_invitations DROP CONSTRAINT clan_invitations_user_id_fkey;
       public          saby_combat_dev    false    219    211    3020            �           2606    54807    clans clans_leader_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.clans
    ADD CONSTRAINT clans_leader_id_fkey FOREIGN KEY (leader_id) REFERENCES public.users(id) ON DELETE CASCADE;
 D   ALTER TABLE ONLY public.clans DROP CONSTRAINT clans_leader_id_fkey;
       public          saby_combat_dev    false    211    3020    213            �           2606    54815    friends friends_friend_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.friends
    ADD CONSTRAINT friends_friend_id_fkey FOREIGN KEY (friend_id) REFERENCES public.users(id) ON DELETE CASCADE;
 H   ALTER TABLE ONLY public.friends DROP CONSTRAINT friends_friend_id_fkey;
       public          saby_combat_dev    false    3020    211    214            �           2606    54820    friends friends_user_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.friends
    ADD CONSTRAINT friends_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;
 F   ALTER TABLE ONLY public.friends DROP CONSTRAINT friends_user_id_fkey;
       public          saby_combat_dev    false    3020    211    214            �           2606    54833 #   user_coins user_coins_level_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.user_coins
    ADD CONSTRAINT user_coins_level_id_fkey FOREIGN KEY (level_id) REFERENCES public.levels(id) ON DELETE SET NULL;
 M   ALTER TABLE ONLY public.user_coins DROP CONSTRAINT user_coins_level_id_fkey;
       public          saby_combat_dev    false    3008    203    216            �           2606    54841 +   user_upgrades user_upgrades_upgrade_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.user_upgrades
    ADD CONSTRAINT user_upgrades_upgrade_id_fkey FOREIGN KEY (upgrade_id) REFERENCES public.upgrades(id) ON DELETE CASCADE;
 U   ALTER TABLE ONLY public.user_upgrades DROP CONSTRAINT user_upgrades_upgrade_id_fkey;
       public          saby_combat_dev    false    205    217    3010            �           2606    54846 (   user_upgrades user_upgrades_user_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.user_upgrades
    ADD CONSTRAINT user_upgrades_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;
 R   ALTER TABLE ONLY public.user_upgrades DROP CONSTRAINT user_upgrades_user_id_fkey;
       public          saby_combat_dev    false    211    217    3020            b      x�K42075K62HL������� )��      t      x������ � �      n      x������ � �      o      x������ � �      d      x������ � �      f      x������ � �      q      x������ � �      h      x������ � �      r      x������ � �      j      x������ � �      l      x������ � �     