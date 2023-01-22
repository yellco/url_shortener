CREATE TABLE public.linksnew(
   id SERIAL PRIMARY KEY,
   link VARCHAR (300)     NOT NULL,
   our_link VARCHAR (300)     NOT NULL,
   addtime TIMESTAMPTZ NOT NULL DEFAULT NOW()
);