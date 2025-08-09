CREATE TYPE "public"."item_type" AS ENUM('email', 'twitter', 'website');--> statement-breakpoint
CREATE TABLE "deai_email" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"processed_item_id" uuid NOT NULL,
	"short_description" text NOT NULL,
	"relevance" text,
	"suggested_action" text,
	"suggested_reply" text DEFAULT '' NOT NULL,
	"message_id" text NOT NULL,
	"subject" text NOT NULL,
	"content" text NOT NULL,
	"type" text NOT NULL,
	"processed_at" timestamp with time zone NOT NULL
);
--> statement-breakpoint
CREATE TABLE "deai_processed_items" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"type" "item_type" NOT NULL,
	"actionable" boolean DEFAULT false NOT NULL,
	"urgency" integer DEFAULT 0 NOT NULL,
	"client_name" text NOT NULL,
	"created_at" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
	"updated_at" timestamp with time zone
);
--> statement-breakpoint
CREATE TABLE "deai_twitter" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"processed_item_id" uuid NOT NULL,
	"short_description" text NOT NULL,
	"relevance" text,
	"suggested_action" text,
	"suggested_reply" text DEFAULT '' NOT NULL,
	"tweet_id" text NOT NULL,
	"url" text NOT NULL,
	"text" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "deai_website" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"processed_item_id" uuid NOT NULL,
	"short_description" text NOT NULL,
	"relevance" text,
	"suggested_action" text,
	"suggested_reply" text DEFAULT '' NOT NULL,
	"url" text NOT NULL,
	"title" text NOT NULL,
	"content" text NOT NULL,
	"opportunity_type" text NOT NULL,
	"read" boolean DEFAULT false NOT NULL,
	"scraped_at" timestamp with time zone NOT NULL
);
--> statement-breakpoint
ALTER TABLE "deai_email" ADD CONSTRAINT "deai_email_processed_item_id_deai_processed_items_id_fk" FOREIGN KEY ("processed_item_id") REFERENCES "public"."deai_processed_items"("id") ON DELETE cascade ON UPDATE cascade;--> statement-breakpoint
ALTER TABLE "deai_twitter" ADD CONSTRAINT "deai_twitter_processed_item_id_deai_processed_items_id_fk" FOREIGN KEY ("processed_item_id") REFERENCES "public"."deai_processed_items"("id") ON DELETE cascade ON UPDATE cascade;--> statement-breakpoint
ALTER TABLE "deai_website" ADD CONSTRAINT "deai_website_processed_item_id_deai_processed_items_id_fk" FOREIGN KEY ("processed_item_id") REFERENCES "public"."deai_processed_items"("id") ON DELETE cascade ON UPDATE cascade;