CREATE TYPE "public"."action_type" AS ENUM('actionable', 'informative', '');--> statement-breakpoint
CREATE TYPE "public"."item_type" AS ENUM('email', 'twitter', 'website');--> statement-breakpoint
ALTER TABLE "deai_processed_items" ALTER COLUMN "type" SET DATA TYPE item_type USING "type"::item_type;;--> statement-breakpoint
ALTER TABLE "deai_email" ADD COLUMN "action_type" "action_type" DEFAULT '';--> statement-breakpoint
ALTER TABLE "deai_twitter" ADD COLUMN "action_type" "action_type" DEFAULT '';--> statement-breakpoint
ALTER TABLE "deai_website" ADD COLUMN "action_type" "action_type" DEFAULT '';