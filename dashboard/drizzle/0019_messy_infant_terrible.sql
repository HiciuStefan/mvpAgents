ALTER TABLE "deai_processed_items" ADD COLUMN "client_name" text NOT NULL;--> statement-breakpoint
ALTER TABLE "deai_email" DROP COLUMN "client_name";--> statement-breakpoint
ALTER TABLE "deai_twitter" DROP COLUMN "client_name";--> statement-breakpoint
ALTER TABLE "deai_website" DROP COLUMN "client_name";