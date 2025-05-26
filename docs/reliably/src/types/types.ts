export interface DocPage {
  title: string;
  description?: string;
  url: string;
  new?: boolean;
  soon?: boolean;
}

export interface Integration {
  name: string;
  description: string;
  category: string;
  svg?: string;
  image?: string;
}
