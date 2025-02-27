import { atom, onMount, onStop } from "nanostores";

export const counter = atom(0);

export function increaseLoaderCounter() {
  counter.set(counter.get() + 1);
};

export function decreaseLoaderCounter() {
  counter.set(counter.get() - 1);
};
