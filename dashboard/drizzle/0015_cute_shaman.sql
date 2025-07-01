ALTER TABLE "deai_twitter" ALTER COLUMN "short_description" SET NOT NULL;--> statement-breakpoint
ALTER TABLE "deai_website" ALTER COLUMN "suggested_action" DROP NOT NULL;--> statement-breakpoint
ALTER TABLE "deai_website" ADD COLUMN "relevance" text;--> statement-breakpoint
ALTER TABLE "deai_twitter" DROP COLUMN "id";--> statement-breakpoint
ALTER TABLE "deai_website" DROP COLUMN "action_type";--> statement-breakpoint
ALTER TABLE "deai_website" DROP COLUMN "created_at";--> statement-breakpoint
ALTER TABLE "deai_website" DROP COLUMN "updated_at";