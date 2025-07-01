ALTER TABLE "deai_twitter" RENAME COLUMN "createdAt" TO "created_at";--> statement-breakpoint
ALTER TABLE "deai_twitter" RENAME COLUMN "updatedAt" TO "updated_at";--> statement-breakpoint
ALTER TABLE "deai_twitter" ADD COLUMN "relevance" text;--> statement-breakpoint
ALTER TABLE "deai_twitter" ADD COLUMN "suggested_action" text;--> statement-breakpoint
ALTER TABLE "deai_twitter" ADD COLUMN "actionable" boolean DEFAULT false;