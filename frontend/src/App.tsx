import { Route, Routes } from "react-router-dom";

import Home from "./pages/Home";
import RepoReport from "./pages/RepoReport";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/projects/:projectId" element={<RepoReport />} />
    </Routes>
  );
}
