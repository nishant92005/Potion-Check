import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, useLocation } from "react-router-dom";
import { AnimatePresence } from "framer-motion";
import App from "./App";
import "./styles.css";

function AnimatedApp() {
  const location = useLocation();
  return (
    <AnimatePresence mode="wait">
      <App key={location.pathname} />
    </AnimatePresence>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <AnimatedApp />
    </BrowserRouter>
  </React.StrictMode>
);
