import { RiBlueskyLine, RiGithubLine, RiMailLine } from "react-icons/ri";
import styles from "./Footer.module.css"
import FeedbackForm from "../FeedbackForm/FeedbackForm";
import { useState } from "react";
import { MdFeedback } from "react-icons/md";

const Footer = () => {
  const [showFeedback, setShowFeedback] = useState(false);
  return (
    <div
      className={styles.footer}
    >
      <a
        href="https://github.com/aebel-shajan"
        target="_blank"
      >
        <RiGithubLine />
        Github
      </a>
      <a
        href="https://bsky.app/profile/aebel.bsky.social"
        target="_blank"
      >
        <RiBlueskyLine />
        Blue sky
      </a>

      <button
      onClick={() => setShowFeedback(true)}
      >
        <MdFeedback />
        Contact
      </button>
      <button
        onClick={() => {
          navigator.clipboard.writeText("aebel.projects@gmail.com");
          alert("Email copied to clipboard!");
        }}
      >
        <RiMailLine />
        email: aebel.projects@gmail.com
      </button>

      {
        showFeedback &&
        <FeedbackForm
          onClose={() => setShowFeedback(false)} />
      }
    </div>
  );
}

export default Footer;