CREATE TABLE IF NOT EXISTS "category" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "user_id" UUID NOT NULL,
    "name" TEXT NOT NULL,
    "total_funds" NUMERIC(11, 2) NOT NULL
);
