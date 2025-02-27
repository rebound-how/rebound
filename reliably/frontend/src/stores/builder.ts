import { atom } from "nanostores";

import type { Configuration } from "@/types/experiments";

export const configurationHolder = atom<Configuration | null>(null);

export async function updateConfigurationHolder(data: Configuration | null) {
  configurationHolder.set(data);
  return configurationHolder.get();
};
