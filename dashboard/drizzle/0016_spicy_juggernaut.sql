ALTER TABLE "deai_email" ALTER COLUMN "suggested_action" DROP NOT NULL;--> statement-breakpoint
ALTER TABLE "deai_email" ADD COLUMN "relevance" text;--> statement-breakpoint
ALTER TABLE "deai_email" DROP COLUMN "action_type";--> statement-breakpoint
ALTER TABLE "deai_email" DROP COLUMN "created_at";--> statement-breakpoint
ALTER TABLE "deai_email" DROP COLUMN "updated_at";