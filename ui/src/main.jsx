import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { lazy, Suspense } from "react";
import App from "./App.jsx";
import { AlertProvider } from "./contexts/AlertContext.jsx";

import "./index.scss";

// Lazy load components
const Coin = lazy(() => import("./Coin.jsx"));

const root = document.getElementById("root");

// Loading component
const LoadingSpinner = () => (
  <div style={{ 
    display: 'flex', 
    justifyContent: 'center', 
    alignItems: 'center', 
    height: '100vh',
    backgroundColor: '#222',
    color: 'white'
  }}>
    <div>Loading...</div>
  </div>
);

ReactDOM.createRoot(root).render(
  <AlertProvider>
    <BrowserRouter>
      <Suspense fallback={<LoadingSpinner />}>
        <Routes>
          <Route path="/" element={<App />} />
          <Route path="/coin/:id" element={<Coin />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  </AlertProvider>
);