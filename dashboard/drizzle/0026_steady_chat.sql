ALTER TABLE "deai_processed_items" ADD COLUMN "urgency" integer DEFAULT 0 NOT NULL;--> statement-breakpoint
ALTER TABLE "deai_email" DROP COLUMN "urgency";--> statement-breakpoint
ALTER TABLE "deai_twitter" DROP COLUMN "urgency";--> statement-breakpoint
ALTER TABLE "deai_website" DROP COLUMN "urgency";