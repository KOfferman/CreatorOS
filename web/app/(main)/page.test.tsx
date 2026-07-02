import { render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import DashboardPage from "./page";

vi.mock("../../lib/api", () => ({
  getActiveUserId: vi.fn().mockReturnValue("test-user"),
  getProfile: vi.fn().mockResolvedValue({
    id: "profile-1",
    user_id: "test-user",
    handle: "creator.test",
    niche: "education",
    bio: "bio",
    target_platforms: ["instagram"],
    creator_voice: "clear",
    audience_size: 1000,
  }),
  getTrends: vi.fn().mockResolvedValue({
    trends: [
      {
        id: "trend-1",
        user_id: "test-user",
        title: "How to build consistent content",
        summary: "Consistency topics are trending.",
        source: "instagram",
        report_date: "2026-07-01",
      },
    ],
  }),
  getIdeas: vi.fn().mockResolvedValue({
    ideas: [
      {
        id: "idea-1",
        user_id: "test-user",
        title: "Post consistency framework",
        description: "desc",
        status: "draft",
        score: 84,
        created_at: "2026-07-01T00:00:00Z",
        updated_at: "2026-07-01T00:00:00Z",
      },
    ],
  }),
  getCalendar: vi.fn().mockResolvedValue({
    items: [
      {
        id: "cal-1",
        user_id: "test-user",
        content_idea_id: "idea-1",
        platform: "instagram",
        scheduled_for: "2026-07-10T09:00:00Z",
        status: "scheduled",
        notes: "Scheduled consistency post",
        created_at: "2026-07-01T00:00:00Z",
        updated_at: "2026-07-01T00:00:00Z",
      },
    ],
  }),
}));

describe("DashboardPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders figma dashboard sections", async () => {
    render(<DashboardPage />);

    await waitFor(() => {
      expect(screen.getByText("This is yours today")).toBeInTheDocument();
    });

    expect(screen.getByText("In your agenda")).toBeInTheDocument();
    expect(screen.getByText("My networks")).toBeInTheDocument();
    expect(screen.getByText("Creator score")).toBeInTheDocument();
  });
});
