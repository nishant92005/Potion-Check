import React, { useEffect, useState } from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, useLocation } from "react-router-dom";
import { AnimatePresence } from "framer-motion";
import App from "./App";
import { StartupLoader } from "./components/StartupLoader";
import "./styles.css";

function AnimatedApp() {
  const location = useLocation();
  const [booting, setBooting] = useState(true);
  const [hidden, setHidden] = useState(false);

  useEffect(() => {
    const bootTimer = window.setTimeout(() => setBooting(false), 2300);
    const hideTimer = window.setTimeout(() => setHidden(true), 2850);
    return () => {
      window.clearTimeout(bootTimer);
      window.clearTimeout(hideTimer);
    };
  }, []);

  return (
    <>
      {!hidden && <StartupLoader done={!booting} />}
      <AnimatePresence mode="wait">
        <App key={location.pathname} />
      </AnimatePresence>
    </>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <AnimatedApp />
    </BrowserRouter>
  </React.StrictMode>
);
