// ------------------------------------------------------------------
// Frontend JavaScript Helper for Twitter Replies
// ------------------------------------------------------------------
// This file contains the JavaScript logic for the frontend application.
// It should be integrated into the Next.js UI by the frontend developer.
// This logic replaces the functionality of the local-only 'reply_helper.py'.
//

/**
 * Opens the target tweet URL in a new tab and copies the reply text 
 * to the clipboard. This function is intended to be called from a 
 * user-initiated event, such as a button click.
 *
 * @param {string} tweetUrl The full URL of the tweet to reply to.
 * @param {string} replyText The text to be copied to the clipboard.
 */
// By adding 'export', we make this function available to be imported
// by other files in the Next.js project, such as a React component.
export const prepareReply = async (tweetUrl, replyText) => {
  // Validate inputs to prevent errors
  if (!tweetUrl || typeof replyText === 'undefined') {
    console.error("Invalid input: tweetUrl and replyText must be provided.");
    return;
  }

  try {
    // Use the modern, asynchronous Clipboard API to copy text.
    // This is more secure and user-friendly.
    await navigator.clipboard.writeText(replyText);

    // Open the tweet URL in a new browser tab.
    // Using '_blank' is important for user experience.
    window.open(tweetUrl, '_blank');

  } catch (error) {
    // Log any errors to the browser's console for debugging.
    // In a production app, this could be replaced with a more
    // user-friendly notification system.
    console.error("Failed to prepare reply:", error);
  }
};

// ------------------------------------------------------------------
// Example Usage in a React Component
// ------------------------------------------------------------------
// The frontend developer can import and use the function like this:

/*
import React from 'react';
// Adjust the path to where this helper file is saved in the frontend project.
import { prepareReply } from './path/to/frontend_reply_helper.js'; 

const TweetCard = ({ tweetData }) => {
  
  // This handler is triggered when the user clicks the 'Reply' button.
  const handleReplyClick = () => {
    // The necessary data (e.g., tweetData.url and tweetData.suggested_reply) 
    // should be available as props passed to the component.
    if (tweetData.url && tweetData.suggested_reply) {
      prepareReply(tweetData.url, tweetData.suggested_reply);
    } else {
      console.error("Missing tweet URL or suggested reply text.");
    }
  };

  return (
    <div className="tweet-card">
      <p>{tweetData.text}</p>
      <button onClick={handleReplyClick}>Reply</button>
    </div>
  );
};
*/
