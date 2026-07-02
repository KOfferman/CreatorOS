"use client";

import { Suspense } from "react";

import { SettingsScreen } from "../../../components/screens/settings-screen";

export default function SettingsPage() {
  return (
    <Suspense fallback={<div className="p-6 text-sm text-[#717182]">Loading settings...</div>}>
      <SettingsScreen />
    </Suspense>
  );
}
