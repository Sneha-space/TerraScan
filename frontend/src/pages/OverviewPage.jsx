import React from "react";
import { Upload } from "lucide-react";
import PageHeader from "../components/layout/PageHeader";
import Button from "../components/common/Button";
import { ErrorNotice, Skeleton } from "../components/common/Feedback";
import {
  AccuracyPanel,
  DistrictPanel,
  PipelinePanel,
  WaitingPanel,
} from "../components/overview/OverviewPanels";
import useApi from "../hooks/useApi";
import { getStats, listRecords } from "../api/endpoints";

export default function OverviewPage() {
  const stats = useApi(() => getStats(), []);
  const waiting = useApi(() => listRecords({ status: "needs_review", limit: 4 }), []);

  return (
    <>
      <PageHeader
        title="Overview"
        description="Where the machine-read land records stand, and what still needs an officer."
        actions={
          <Button to="/uploads">
            <Upload className="h-4 w-4" aria-hidden="true" />
            Upload a file
          </Button>
        }
      />

      {stats.error && <ErrorNotice message={stats.error} onRetry={stats.reload} />}

      {stats.loading && (
        <div className="space-y-6" role="status" aria-label="Loading">
          <Skeleton className="h-56 w-full" />
          <div className="grid gap-6 lg:grid-cols-2">
            <Skeleton className="h-64" />
            <Skeleton className="h-64" />
          </div>
        </div>
      )}

      {stats.data && (
        <div className="space-y-6">
          <PipelinePanel stats={stats.data} />
          <div className="grid gap-6 lg:grid-cols-2">
            <AccuracyPanel stats={stats.data} />
            <DistrictPanel stats={stats.data} />
          </div>
          {waiting.data && (
            <WaitingPanel records={waiting.data} threshold={stats.data.confidence_threshold} />
          )}
        </div>
      )}
    </>
  );
}
