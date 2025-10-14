ALTER TABLE "agents"."users" ADD COLUMN "is_active" boolean DEFAULT true;
ALTER TABLE "agents"."users" ADD COLUMN "webhook" boolean DEFAULT false;
