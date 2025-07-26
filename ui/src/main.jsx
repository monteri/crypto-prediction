import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import App from "./App.jsx";
import Coin from "./Coin.jsx";

import "./index.scss";

const root = document.getElementById("root");

ReactDOM.createRoot(root).render(
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<App />} />
      <Route path="/coin/:id" element={<Coin />} />
      <Route path="/about" element={<h2 style={{ color: "white" }}>About page</h2>} />
    </Routes>
  </BrowserRouter>
);