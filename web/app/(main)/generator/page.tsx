"use client";

import { Suspense } from "react";

import { GeneratorScreen } from "../../../components/screens/generator-screen";

export default function GeneratorPage() {
  return (
    <Suspense fallback={<div className="text-sm text-[#717182]">Loading generator...</div>}>
      <GeneratorScreen />
    </Suspense>
  );
}
