import React from "react";
import ReactDOM from "react-dom/client";

// bundled with the app, so the fonts load without internet access
import "@fontsource-variable/anek-latin/wdth.css";
import "@fontsource-variable/anek-bangla/wdth.css";
import "@fontsource-variable/anek-devanagari/wdth.css";

import App from "./App.jsx";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
