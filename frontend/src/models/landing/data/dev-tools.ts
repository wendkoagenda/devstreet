const DEVICON = "https://cdn.jsdelivr.net/gh/devicons/devicon@v2.18.0/icons";
const SI = "https://cdn.simpleicons.org";
const SI_JS = "https://cdn.jsdelivr.net/npm/simple-icons@v13/icons";

export type DevTool = {
  name: string;
  logo: string;
  /** Logo monochrome sombre : inversé en thème sombre pour rester lisible. */
  mono?: boolean;
};

/** Gauche : IA + éditeurs. */
export const LEFT_TOOLS: DevTool[] = [
  { name: "Claude", logo: `${SI}/claude` },
  { name: "ChatGPT", logo: `${SI_JS}/openai.svg`, mono: true },
  { name: "Gemini", logo: `${SI}/googlegemini` },
  { name: "GitHub Copilot", logo: `${SI}/githubcopilot`, mono: true },
  { name: "Cursor", logo: `${SI}/cursor`, mono: true },
  { name: "VS Code", logo: `${DEVICON}/vscode/vscode-original.svg` },
];

/** Droite : no-code / side tools + stack. */
export const RIGHT_TOOLS: DevTool[] = [
  { name: "Make", logo: `${SI}/make` },
  { name: "n8n", logo: `${SI}/n8n` },
  { name: "Zapier", logo: `${SI}/zapier` },
  { name: "Notion", logo: `${SI}/notion`, mono: true },
  { name: "Figma", logo: `${DEVICON}/figma/figma-original.svg` },
  { name: "Python", logo: `${DEVICON}/python/python-original.svg` },
];
