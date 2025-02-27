export function contributionToNumber(contribution: string): number | null {
  let contributionAsNumber: number | null = null;
  switch (contribution) {
    case "none":
      contributionAsNumber = 0;
      break;
    case "low":
      contributionAsNumber = 1;
      break;
    case "medium":
      contributionAsNumber = 2;
      break;
    case "high":
      contributionAsNumber = 3;
      break;
  }
  return contributionAsNumber;
}

export function contributionToString(contribution: string | number) {
  let contributionAsString: string = "";
  let contributionNumber: number | null = null;
  if (typeof contribution === "string") {
    contributionNumber = Number(contribution);
  } else {
    contributionNumber = contribution;
  }
  if (contributionNumber !== null) {
    switch (contributionNumber) {
      case 0:
        contributionAsString = "none";
        break;
      case 1:
        contributionAsString = "low";
        break;
      case 2:
        contributionAsString = "medium";
        break;
      case 3:
        contributionAsString = "high";
        break;
    }
  }
  return contributionAsString;
}
