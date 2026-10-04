import React from "react";
import { BrowserRouter, Outlet, Route, Routes } from "react-router-dom";
import AppShell from "./components/layout/AppShell";
import Button from "./components/common/Button";
import { EmptyState } from "./components/common/Feedback";
import OverviewPage from "./pages/OverviewPage";
import ReviewQueuePage from "./pages/ReviewQueuePage";
import RecordsPage from "./pages/RecordsPage";
import UploadsPage from "./pages/UploadsPage";
import ReviewPage from "./pages/ReviewPage";

// list pages read best at a limited width; the review page uses the full
// width to put the scan beside the fields
function Contained() {
  return (
    <div className="mx-auto max-w-[76rem]">
      <Outlet />
    </div>
  );
}

function NotFound() {
  return (
    <EmptyState title="There's no page here" action={<Button to="/">Go to overview</Button>}>
      The link may be old, or the record may have been removed.
    </EmptyState>
  );
}

export default function App() {
  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <Routes>
        <Route element={<AppShell />}>
          <Route element={<Contained />}>
            <Route index element={<OverviewPage />} />
            <Route path="review" element={<ReviewQueuePage />} />
            <Route path="records" element={<RecordsPage />} />
            <Route path="uploads" element={<UploadsPage />} />
            <Route path="*" element={<NotFound />} />
          </Route>
          <Route path="records/:recordId" element={<ReviewPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
