ALTER TABLE "deai_twitter" ADD COLUMN "id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL;--> statement-breakpoint
DROP TYPE "public"."action_type";