import { useEffect, useState } from "react";

export function useTypewriter(phrases, typeSpeed = 50, deleteSpeed = 30, pause = 2000) {
  const [text, setText] = useState("");
  const [index, setIndex] = useState(0);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    const phrase = phrases[index % phrases.length];
    const doneTyping = !deleting && text === phrase;
    const doneDeleting = deleting && text === "";
    const delay = doneTyping ? pause : deleting ? deleteSpeed : typeSpeed;
    const timer = window.setTimeout(() => {
      if (doneTyping) setDeleting(true);
      else if (doneDeleting) {
        setDeleting(false);
        setIndex((value) => value + 1);
      } else {
        setText(phrase.slice(0, deleting ? text.length - 1 : text.length + 1));
      }
    }, delay);
    return () => window.clearTimeout(timer);
  }, [deleteSpeed, deleting, index, pause, phrases, text, typeSpeed]);

  return text;
}
