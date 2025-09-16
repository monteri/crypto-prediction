import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { AlertProvider } from "./contexts/AlertContext.jsx";
import Router from "./Router.jsx";

import "./index.scss";

const root = document.getElementById("root");

ReactDOM.createRoot(root).render(
  <AlertProvider>
    <BrowserRouter>
      <Router />
    </BrowserRouter>
  </AlertProvider>
);