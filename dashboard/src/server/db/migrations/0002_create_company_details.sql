CREATE TABLE "agents"."company_details" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"created_by_user_id" uuid,
	"updated_by_user_id" uuid,
	"deleted_at" timestamp with time zone,
	"user_id" uuid NOT NULL,
	"company_name" text NOT NULL,
	"industry" text NOT NULL,
	"company_description" text NOT NULL,
	"website" text
);
--> statement-breakpoint
ALTER TABLE "agents"."company_details" ADD CONSTRAINT "company_details_created_by_user_id_users_id_fk" FOREIGN KEY ("created_by_user_id") REFERENCES "agents"."users"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "agents"."company_details" ADD CONSTRAINT "company_details_updated_by_user_id_users_id_fk" FOREIGN KEY ("updated_by_user_id") REFERENCES "agents"."users"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "agents"."company_details" ADD CONSTRAINT "company_details_user_id_users_id_fk" FOREIGN KEY ("user_id") REFERENCES "agents"."users"("id") ON DELETE cascade ON UPDATE cascade;--> statement-breakpoint
CREATE INDEX "company_details_created_at_idx" ON "agents"."company_details" USING btree ("created_at");
