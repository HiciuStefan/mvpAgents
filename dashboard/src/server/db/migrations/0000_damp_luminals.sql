CREATE SCHEMA "agents";
--> statement-breakpoint
CREATE TABLE "agents"."users" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"clerk_id" text NOT NULL,
	"email" text,
	"first_name" text,
	"last_name" text,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"deleted_at" timestamp with time zone,
	CONSTRAINT "users_clerk_id_unique" UNIQUE("clerk_id"),
	CONSTRAINT "users_email_unique" UNIQUE("email")
);
--> statement-breakpoint
CREATE TABLE "agents"."partners" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"created_by_user_id" uuid,
	"updated_by_user_id" uuid,
	"deleted_at" timestamp with time zone,
	"user_id" uuid NOT NULL,
	"name" text NOT NULL,
	"description" text
);
--> statement-breakpoint
CREATE TABLE "agents"."processed_items" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"created_by_user_id" uuid,
	"updated_by_user_id" uuid,
	"deleted_at" timestamp with time zone,
	"type" text NOT NULL,
	"actionable" boolean DEFAULT false NOT NULL,
	"urgency" integer DEFAULT 0 NOT NULL,
	"client_name" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "agents"."email" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"created_by_user_id" uuid,
	"updated_by_user_id" uuid,
	"deleted_at" timestamp with time zone,
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
CREATE TABLE "agents"."twitter" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"created_by_user_id" uuid,
	"updated_by_user_id" uuid,
	"deleted_at" timestamp with time zone,
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
CREATE TABLE "agents"."website" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"created_by_user_id" uuid,
	"updated_by_user_id" uuid,
	"deleted_at" timestamp with time zone,
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
ALTER TABLE "agents"."partners" ADD CONSTRAINT "partners_created_by_user_id_users_id_fk" FOREIGN KEY ("created_by_user_id") REFERENCES "agents"."users"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "agents"."partners" ADD CONSTRAINT "partners_updated_by_user_id_users_id_fk" FOREIGN KEY ("updated_by_user_id") REFERENCES "agents"."users"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "agents"."partners" ADD CONSTRAINT "partners_user_id_users_id_fk" FOREIGN KEY ("user_id") REFERENCES "agents"."users"("id") ON DELETE cascade ON UPDATE cascade;--> statement-breakpoint
ALTER TABLE "agents"."processed_items" ADD CONSTRAINT "processed_items_created_by_user_id_users_id_fk" FOREIGN KEY ("created_by_user_id") REFERENCES "agents"."users"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "agents"."processed_items" ADD CONSTRAINT "processed_items_updated_by_user_id_users_id_fk" FOREIGN KEY ("updated_by_user_id") REFERENCES "agents"."users"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "agents"."email" ADD CONSTRAINT "email_created_by_user_id_users_id_fk" FOREIGN KEY ("created_by_user_id") REFERENCES "agents"."users"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "agents"."email" ADD CONSTRAINT "email_updated_by_user_id_users_id_fk" FOREIGN KEY ("updated_by_user_id") REFERENCES "agents"."users"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "agents"."email" ADD CONSTRAINT "email_processed_item_id_processed_items_id_fk" FOREIGN KEY ("processed_item_id") REFERENCES "agents"."processed_items"("id") ON DELETE cascade ON UPDATE cascade;--> statement-breakpoint
ALTER TABLE "agents"."twitter" ADD CONSTRAINT "twitter_created_by_user_id_users_id_fk" FOREIGN KEY ("created_by_user_id") REFERENCES "agents"."users"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "agents"."twitter" ADD CONSTRAINT "twitter_updated_by_user_id_users_id_fk" FOREIGN KEY ("updated_by_user_id") REFERENCES "agents"."users"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "agents"."twitter" ADD CONSTRAINT "twitter_processed_item_id_processed_items_id_fk" FOREIGN KEY ("processed_item_id") REFERENCES "agents"."processed_items"("id") ON DELETE cascade ON UPDATE cascade;--> statement-breakpoint
ALTER TABLE "agents"."website" ADD CONSTRAINT "website_created_by_user_id_users_id_fk" FOREIGN KEY ("created_by_user_id") REFERENCES "agents"."users"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "agents"."website" ADD CONSTRAINT "website_updated_by_user_id_users_id_fk" FOREIGN KEY ("updated_by_user_id") REFERENCES "agents"."users"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "agents"."website" ADD CONSTRAINT "website_processed_item_id_processed_items_id_fk" FOREIGN KEY ("processed_item_id") REFERENCES "agents"."processed_items"("id") ON DELETE cascade ON UPDATE cascade;--> statement-breakpoint
CREATE INDEX "partners_created_at_idx" ON "agents"."partners" USING btree ("created_at");--> statement-breakpoint
CREATE INDEX "processed_items_created_at_idx" ON "agents"."processed_items" USING btree ("created_at");--> statement-breakpoint
CREATE INDEX "email_created_at_idx" ON "agents"."email" USING btree ("created_at");--> statement-breakpoint
CREATE INDEX "twitter_created_at_idx" ON "agents"."twitter" USING btree ("created_at");--> statement-breakpoint
CREATE INDEX "tweet_id_idx" ON "agents"."twitter" USING btree ("tweet_id");--> statement-breakpoint
CREATE INDEX "website_created_at_idx" ON "agents"."website" USING btree ("created_at");