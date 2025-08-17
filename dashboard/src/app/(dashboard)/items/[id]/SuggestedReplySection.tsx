"use client";

import { useState } from "react";
import { Textarea } from "~/components/ui/textarea";
import { Button } from "~/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "~/components/ui/card";
import type { LatestItem } from "~/server/db/fetch_items";
import { ReplyIcon, SendIcon } from "lucide-react";
import { XSVG } from "~/components/ChannelBadge";

interface SuggestedReplySectionProps {
  item: LatestItem;
}

// Type guards for different item types
interface WebsiteData {
  title: string;
  url: string;
  content: string;
  opportunity_type: string;
  read: boolean;
  scraped_at: Date;
  suggested_reply: string;
  short_description: string;
  [key: string]: unknown;
}

interface EmailData {
  subject: string;
  content: string;
  type: string;
  message_id: string;
  processed_at: Date;
  suggested_reply: string;
  short_description: string;
  [key: string]: unknown;
}

// Utility function to open Twitter reply intent
function openTwitterReply(tweetId: string, text: string) {
  const encodedText = encodeURIComponent(text);
  const url = `https://x.com/intent/tweet?in_reply_to=${tweetId}&text=${encodedText}`;
  window.open(url, "_blank");
}

// Utility function to open Twitter compose
function openTwitterCompose(text: string) {
  const encodedText = encodeURIComponent(text);
  const url = `https://x.com/intent/tweet?text=${encodedText}`;
  window.open(url, "_blank");
}

// Utility function to open email compose
function openEmailCompose(subject: string, body: string) {
  const encodedSubject = encodeURIComponent(subject);
  const encodedBody = encodeURIComponent(body);
  const url = `mailto:?subject=${encodedSubject}&body=${encodedBody}`;
  window.open(url, "_self");
}

// Utility function to open email reply
function openEmailReply(item: LatestItem, replyText: string) {
  if (item.type === "email") {
    const emailData = item.data as EmailData;
    const originalSubject = emailData.subject;

    // Add "Re: " prefix if not already present
    const replySubject = originalSubject.startsWith("Re: ")
      ? originalSubject
      : `Re: ${originalSubject}`;

    const encodedSubject = encodeURIComponent(replySubject);
    const encodedBody = encodeURIComponent(replyText);

    // Use mailto with In-Reply-To header for proper email threading
    const url = `mailto:?subject=${encodedSubject}&body=${encodedBody}`;
    window.open(url, "_self");
  }
}

export default function SuggestedReplySection({ item }: SuggestedReplySectionProps) {
  const [suggestedReply, setSuggestedReply] = useState(item.data?.suggested_reply ?? "");

  const handleReplyToTweet = () => {
    if (item.type === "twitter" && item.data?.tweet_id) {
      const tweetId = item.data.tweet_id;
      if (tweetId) {
        openTwitterReply(tweetId, suggestedReply);
      } else {
        alert("Could not extract tweet ID from URL");
      }
    }
  };

  const handleReplyToEmail = () => {
    openEmailReply(item, suggestedReply);
  };

  const handlePostTweet = () => {
    openTwitterCompose(suggestedReply);
  };

  const handleSendEmail = () => {
    let subject = "Re: ";
    if (item.type === "website") {
      const websiteData = item.data as WebsiteData;
      subject += websiteData.title ?? websiteData.short_description ?? "";
    } else if (item.type === "email") {
      const emailData = item.data as EmailData;
      subject += emailData.subject ?? emailData.short_description ?? "";
    } else {
      subject += item.data?.short_description ?? "";
    }
    openEmailCompose(subject, suggestedReply);
  };

  return (
    <div className="space-y-4">
      {/* Suggested Reply Section */}
      <Card className="border-0 shadow-none py-0 gap-0">
        <CardHeader className="gap-0 px-0 border border-b-0 rounded-tl-lg rounded-tr-lg">
          <CardTitle className="px-4 py-3 text-md font-medium flex items-center gap-2">
            Suggested Reply
          </CardTitle>
        </CardHeader>
        <CardContent className="px-0">
          <Textarea
            value={suggestedReply}
            onChange={(e) => setSuggestedReply(e.target.value)}
            placeholder=""
            className="min-h-[200px] bg-white border focus-visible:ring-blue-500"
          />
        </CardContent>
      </Card>

      {/* Action Buttons */}
      <div className="flex flex-wrap gap-2">
        {item.type === "twitter" && (
          <ReplyButton
            onClick={handleReplyToTweet}
            disabled={suggestedReply.trim() === ""}
          >
						<ReplyIcon className="size-4" strokeWidth={1.5} />
            Reply to Tweet
          </ReplyButton>
        )}

        {item.type === "email" && (
          <ReplyButton
            onClick={handleReplyToEmail}
            disabled={suggestedReply.trim() === ""}
          >
						<ReplyIcon className="size-4" strokeWidth={1.5} />
            Reply to Email
          </ReplyButton>
        )}

        {item.type === "website" && (
          <>
            <ReplyButton
              onClick={handlePostTweet}
              disabled={suggestedReply.trim() === ""}
            >
							<XSVG size={16} />
              Post Tweet
            </ReplyButton>
            <ReplyButton
              onClick={handleSendEmail}
              disabled={suggestedReply.trim() === ""}
            >
							<SendIcon className="size-4" strokeWidth={1.5} />
              Send Email
            </ReplyButton>
          </>
        )}
      </div>
    </div>
  );
}


function ReplyButton({ onClick, disabled, children }: { onClick: () => void, disabled: boolean, children: React.ReactNode }) {
  return (
    <Button
      onClick={onClick}
      className="flex items-center"
      variant="outline"
      disabled={disabled}
    >
      {/* <MessageSquare className="size-4" strokeWidth={2} /> */}
      {children}
    </Button>
  );
}
