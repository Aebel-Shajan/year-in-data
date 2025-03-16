import { useState } from "react";
import styles from "./FeedbackForm.module.css"
import Modal from "./Modal/Modal"

interface FeedbackFormProps {
  onClose: CallableFunction
}

const FeedbackForm = (
  {
    onClose
  }: FeedbackFormProps
) => {
  const [result, setResult] = useState("");

  const onSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setResult("Sending....");
    const formData = new FormData(event.target as HTMLFormElement);

    formData.append("access_key", "86168a8b-2a69-46e2-800e-8016f5907618");

    const response = await fetch("https://api.web3forms.com/submit", {
      method: "POST",
      body: formData
    });

    const data = await response.json();

    if (data.success) {
      setResult("Form Submitted Successfully");
      (event.target as HTMLFormElement).reset();
      onClose()
    } else {
      console.log("Error", data);
      setResult(data.message);
    }
  };

  return (
    <Modal onClose={onClose}>

      <div className={styles.feedbackContainer}>

        <h1
          className={styles.title}
        >
          Contact form
        </h1>

        <form
          className={styles.feedbackForm}
          onSubmit={onSubmit}
        >
          <div>
            <label>Name</label>
            <input type="text" name="name" required />
          </div>
          <div>
            <label>Email</label>
            <input 
              type="email"
              name="email"
               />
          </div>
          <div>
            <label>Feedback</label>
            <textarea
              name="message"
              required
              placeholder="Contact me about anything....."
            ></textarea>
          </div>
          <button
            style={{ width: "100%" }}
            type="submit">
            Submit Form
          </button>
        </form>
        <span style={{ color: "white" }}>{result}</span>
      </div>
    </Modal>

  );
}

export default FeedbackForm;