ALTER TABLE "deai_email" ADD COLUMN "urgency" integer DEFAULT 0 NOT NULL;--> statement-breakpoint
ALTER TABLE "deai_processed_items" ADD COLUMN "client_name" text NOT NULL;--> statement-breakpoint
ALTER TABLE "deai_twitter" ADD COLUMN "urgency" integer DEFAULT 0 NOT NULL;--> statement-breakpoint
ALTER TABLE "deai_website" ADD COLUMN "urgency" integer DEFAULT 0 NOT NULL;--> statement-breakpoint
ALTER TABLE "deai_email" DROP COLUMN "client_name";--> statement-breakpoint
ALTER TABLE "deai_twitter" DROP COLUMN "client_name";--> statement-breakpoint
ALTER TABLE "deai_website" DROP COLUMN "client_name";