export function readingTime(words: number) {
  const wpm = 225;
  // const words = post.trim().split(/\s+/).length;
  const time = Math.ceil(words / wpm);
  return time;
}
