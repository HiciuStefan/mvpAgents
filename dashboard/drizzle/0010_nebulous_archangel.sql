ALTER TABLE "deai_email" RENAME COLUMN "company_name" TO "client_name";--> statement-breakpoint
ALTER TABLE "deai_twitter" ALTER COLUMN "reply" SET DEFAULT '';--> statement-breakpoint
ALTER TABLE "deai_twitter" DROP COLUMN "category";--> statement-breakpoint
ALTER TABLE "deai_twitter" DROP COLUMN "company_name";--> statement-breakpoint
ALTER TABLE "deai_website" DROP COLUMN "label";--> statement-breakpoint
ALTER TABLE "deai_website" DROP COLUMN "company_name";