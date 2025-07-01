ALTER TABLE "deai_email" ADD COLUMN "client_name" text NOT NULL;--> statement-breakpoint
ALTER TABLE "deai_twitter" ADD COLUMN "client_name" text NOT NULL;--> statement-breakpoint
ALTER TABLE "deai_website" ADD COLUMN "client_name" text NOT NULL;--> statement-breakpoint
ALTER TABLE "deai_processed_items" DROP COLUMN "client_name";