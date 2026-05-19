import { Route, Routes } from "react-router-dom";
import { AnimatedBackground } from "./components/AnimatedBackground";
import { CustomCursor } from "./components/CustomCursor";
import { Navbar } from "./components/Navbar";
import { ToastHost } from "./components/ToastHost";
import Landing from "./pages/Landing";
import Profile from "./pages/Profile";
import Scanner from "./pages/Scanner";
import Analysis from "./pages/Analysis";
import History from "./pages/History";
import About from "./pages/About";
import Developer from "./pages/Developer";

export default function App() {
  return (
    <>
      <AnimatedBackground />
      <CustomCursor />
      <Navbar />
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/scanner" element={<Scanner />} />
        <Route path="/analysis/:productId" element={<Analysis />} />
        <Route path="/history" element={<History />} />
        <Route path="/about" element={<About />} />
        <Route path="/developer" element={<Developer />} />
      </Routes>
      <ToastHost />
    </>
  );
}
