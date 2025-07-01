ALTER TABLE "deai_email" ADD COLUMN "message_id" text DEFAULT '' NOT NULL;--> statement-breakpoint
ALTER TABLE "deai_email" ADD COLUMN "short_description" text DEFAULT '' NOT NULL;--> statement-breakpoint
ALTER TABLE "deai_email" ADD COLUMN "company_name" text DEFAULT '' NOT NULL;--> statement-breakpoint
ALTER TABLE "deai_twitter" ADD COLUMN "short_description" text DEFAULT '' NOT NULL;--> statement-breakpoint
ALTER TABLE "deai_twitter" ADD COLUMN "company_name" text DEFAULT '' NOT NULL;--> statement-breakpoint
ALTER TABLE "deai_website" ADD COLUMN "short_description" text DEFAULT '' NOT NULL;--> statement-breakpoint
ALTER TABLE "deai_website" ADD COLUMN "company_name" text DEFAULT '' NOT NULL;