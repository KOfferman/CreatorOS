"use client";

import { useEffect, useState } from "react";
import { Eye, Heart, MessageCircle, MoreHorizontal, Plus } from "lucide-react";

import { getActiveUserId, getIdeas, type ContentIdea } from "../../lib/api";
import { IgIcon } from "../ui/platform-icons";

export function PostsScreen() {
  const [filter, setFilter] = useState("All");
  const [ideas, setIdeas] = useState<ContentIdea[]>([]);

  useEffect(() => {
    void getIdeas(getActiveUserId())
      .then((result) => setIdeas(result.ideas))
      .catch(() => setIdeas([]));
  }, []);

  const filtered = ideas.filter((idea) => {
    if (filter === "All") return true;
    if (filter === "Drafts") return idea.status === "draft";
    return idea.status === filter.toLowerCase();
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="mb-1 text-[1.65rem] font-extrabold text-white">Posts</h1>
          <p className="text-sm text-[#717182]">All your published & scheduled content</p>
        </div>
        <button
          type="button"
          className="flex items-center gap-2 rounded-xl bg-violet-600 px-4 py-2 text-sm font-semibold text-white transition-all hover:bg-violet-500"
        >
          <Plus size={14} />
          New Post
        </button>
      </div>
      <div className="flex flex-wrap gap-2">
        {["All", "Published", "Scheduled", "Drafts"].map((f) => (
          <button
            key={f}
            type="button"
            onClick={() => setFilter(f)}
            className={`rounded-full px-4 py-1.5 text-sm font-medium transition-all ${
              filter === f ? "bg-violet-600 text-white" : "bg-white/5 text-[#717182] hover:text-white"
            }`}
          >
            {f}
          </button>
        ))}
      </div>
      <div className="space-y-3">
        {filtered.map((post) => (
          <div
            key={post.id}
            className="flex items-center gap-4 rounded-2xl border border-white/5 bg-[#0F0F1C] p-5 transition-all hover:border-white/10"
          >
            <div className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500/15 to-pink-500/15">
              <IgIcon size={22} />
            </div>
            <div className="min-w-0 flex-1">
              <p className="mb-0.5 truncate text-sm font-semibold text-white">{post.title}</p>
              <p className="text-xs text-[#717182]">{new Date(post.created_at).toLocaleDateString()}</p>
            </div>
            <div className="hidden items-center gap-5 text-xs text-[#717182] md:flex">
              <span className="flex items-center gap-1">
                <Eye size={11} />
                {post.score ? `${Math.round(post.score)}K` : "—"}
              </span>
              <span className="flex items-center gap-1">
                <Heart size={11} />
                {post.score ? `${Math.round(post.score / 2)}K` : "—"}
              </span>
              <span className="flex items-center gap-1">
                <MessageCircle size={11} />
                {post.score ? `${Math.round(post.score / 10)}` : "—"}
              </span>
            </div>
            <span className="flex-shrink-0 rounded-full border border-emerald-500/20 bg-emerald-500/15 px-2.5 py-1 text-[11px] font-medium capitalize text-emerald-300">
              {post.status}
            </span>
            <button type="button" className="flex-shrink-0 text-[#717182] transition-colors hover:text-white">
              <MoreHorizontal size={15} />
            </button>
          </div>
        ))}
        {!filtered.length ? <p className="text-sm text-[#717182]">No posts yet.</p> : null}
      </div>
    </div>
  );
}
