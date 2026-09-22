import React from "react";
import { Link } from "react-router-dom";
import useDashboard from "../hooks/useDashboard";
import StatusCards from "../components/dashboard/StatusCards";
import RecordList from "../components/dashboard/RecordList";
import Button from "../components/common/Button";
import { StatusCardsSkeleton, RecordListSkeleton } from "../components/common/Skeleton";

export default function DashboardPage() {
  const { data, loading, error, refetch } = useDashboard();

  if (loading) {
    return (
      <div className="space-y-8">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold text-gray-900">Dashboard</h1>
            <p className="text-sm text-gray-500 mt-1">
              Overview of land records processing
            </p>
          </div>
        </div>
        <StatusCardsSkeleton />
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <RecordListSkeleton />
          <RecordListSkeleton />
          <RecordListSkeleton />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-lg mx-auto mt-20 text-center">
        <div className="bg-rose-50 text-rose-700 rounded-2xl p-6 border border-rose-100">
          <p className="font-medium mb-2">Could not load dashboard</p>
          <p className="text-sm mb-4">{error}</p>
          <Button onClick={refetch} variant="secondary" size="sm">
            Try again
          </Button>
        </div>
      </div>
    );
  }

  const counts = data?.status_counts || {};
  const needsReview = data?.needs_review || [];
  const autoApproved = data?.auto_approved || [];
  const verified = data?.verified || [];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Dashboard</h1>
          <p className="text-sm text-gray-500 mt-1">
            Overview of land records processing
          </p>
        </div>
        <Link to="/upload">
          <Button>
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Upload Record
          </Button>
        </Link>
      </div>

      {/* Status Cards */}
      <StatusCards counts={counts} />

      {/* Lists — same order as the status cards above */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <RecordList
          title="Needs Review"
          records={needsReview}
          emptyTitle="No records need review"
          emptyDescription="All caught up! Upload a new document to get started."
        />
        <RecordList
          title="Auto Approved"
          records={autoApproved}
          emptyTitle="No auto-approved records"
          emptyDescription="Records the system approves without review will appear here."
        />
        <RecordList
          title="Verified"
          records={verified}
          emptyTitle="No verified records yet"
          emptyDescription="Verified records will appear here after review."
        />
      </div>
    </div>
  );
}

