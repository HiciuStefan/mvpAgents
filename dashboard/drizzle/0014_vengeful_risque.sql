ALTER TABLE "deai_processed_items" RENAME COLUMN "is_actionable" TO "actionable";--> statement-breakpoint
ALTER TABLE "deai_twitter" ALTER COLUMN "short_description" DROP NOT NULL;--> statement-breakpoint
ALTER TABLE "deai_twitter" DROP COLUMN "created_at";--> statement-breakpoint
ALTER TABLE "deai_twitter" DROP COLUMN "updated_at";--> statement-breakpoint
ALTER TABLE "deai_twitter" DROP COLUMN "actionable";--> statement-breakpoint
ALTER TABLE "deai_twitter" DROP COLUMN "action_type";