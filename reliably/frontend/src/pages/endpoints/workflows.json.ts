import type { Activity } from "@/types/ui-types";

export async function GET({ params, request }) {
//export function get() {
  const activities = Object.values(
    import.meta.glob("../experiments/workflows/*.{md,mdx}", { eager: true })
  );
  const activitiesArr: Activity[] = [];
  activities.forEach((a) => {
    const ac = a as any;
    // const moduleArr = ac.frontmatter.module.split(".");
    const urlArr: string[] = ac.url.split("/");
    activitiesArr.push({
      id: urlArr[3],
      name: ac.frontmatter.name,
      target: ac.frontmatter.target,
      category: ac.frontmatter.category,
      type: ac.frontmatter.type,
      description: ac.frontmatter.description,
      module: ac.frontmatter.module,
    });
  });
  activitiesArr.sort((a, b) => {
    return a.name <= b.name ? -1 : 1;
  });
  return new Response(
    JSON.stringify({
      activities: activitiesArr,
    }),
  );
}
