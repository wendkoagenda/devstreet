/**
 * Profils de vitrine fictifs et anonymisés : aucun ne correspond à un compte réel.
 * Les photos viennent de l'API de portraits de démonstration randomuser.me.
 */
const PORTRAIT_API = "https://randomuser.me/api/portraits";
export type DevStatus = "available" | "mission" | "open";

export type CompanySector =
  | "fintech"
  | "healthtech"
  | "logistics"
  | "agritech"
  | "edtech"
  | "ecommerce"
  | "cleantech"
  | "saas"
  | "telecom"
  | "insurtech"
  | "ai"
  | "mobility";

export type ConnectionEvent = "match" | "mission" | "pr" | "answer" | "application" | "help";

export type DevProfile = {
  id: string;
  name: string;
  initials: string;
  role: string;
  stack: string[];
  years: number;
  photo: string;
  city: string;
  country: string;
  status: DevStatus;
  lat: number;
  lon: number;
};

export type CompanyProfile = {
  id: string;
  name: string;
  initials: string;
  sector: CompanySector;
  teamSize: number;
  openRoles: number;
  seeking: string[];
  city: string;
  country: string;
  lat: number;
  lon: number;
};

export type GlobeMarkerKind = "dev" | "company";

export type GlobeMarker = {
  lat: number;
  lon: number;
  kind: GlobeMarkerKind;
};

export type GlobeConnection = {
  id: string;
  dev: DevProfile;
  company: CompanyProfile;
  event: ConnectionEvent;
  score?: number;
};

export const DEV_PROFILES: DevProfile[] = [
  { id: "awa", name: "Awa D.", initials: "AD", role: "Backend", stack: ["Django", "PostgreSQL", "Docker"], years: 5, photo: `${PORTRAIT_API}/women/16.jpg`, city: "Dakar", country: "SN", status: "available", lat: 14.72, lon: -17.45 },
  { id: "wendyam", name: "Wendyam S.", initials: "WS", role: "Fullstack", stack: ["React", "Node.js", "Prisma"], years: 4, photo: `${PORTRAIT_API}/men/53.jpg`, city: "Ouagadougou", country: "BF", status: "available", lat: 12.37, lon: -1.53 },
  { id: "tunde", name: "Tunde A.", initials: "TA", role: "Mobile", stack: ["Flutter", "Firebase", "Dart"], years: 6, photo: `${PORTRAIT_API}/men/54.jpg`, city: "Lagos", country: "NG", status: "open", lat: 6.52, lon: 3.38 },
  { id: "grace", name: "Grace W.", initials: "GW", role: "Data engineer", stack: ["Python", "Airflow", "dbt"], years: 7, photo: `${PORTRAIT_API}/women/36.jpg`, city: "Nairobi", country: "KE", status: "mission", lat: -1.29, lon: 36.82 },
  { id: "yasmine", name: "Yasmine E.", initials: "YE", role: "Frontend", stack: ["Vue", "TypeScript", "Vite"], years: 3, photo: `${PORTRAIT_API}/women/26.jpg`, city: "Casablanca", country: "MA", status: "available", lat: 33.57, lon: -7.59 },
  { id: "kofi", name: "Kofi M.", initials: "KM", role: "DevOps", stack: ["Kubernetes", "Terraform", "GitLab CI"], years: 8, photo: `${PORTRAIT_API}/men/16.jpg`, city: "Accra", country: "GH", status: "available", lat: 5.6, lon: -0.19 },
  { id: "karim", name: "Karim B.", initials: "KB", role: "Machine learning", stack: ["PyTorch", "MLOps", "Streamlit"], years: 6, photo: `${PORTRAIT_API}/men/5.jpg`, city: "Tunis", country: "TN", status: "open", lat: 36.8, lon: 10.18 },
  { id: "jean-paul", name: "Jean-Paul K.", initials: "JK", role: "Backend", stack: ["Go", "gRPC", "Redis"], years: 9, photo: `${PORTRAIT_API}/men/80.jpg`, city: "Kinshasa", country: "CD", status: "mission", lat: -4.44, lon: 15.27 },
  { id: "thandiwe", name: "Thandiwe N.", initials: "TN", role: "Cloud", stack: ["AWS", "Serverless", "Python"], years: 5, photo: `${PORTRAIT_API}/women/92.jpg`, city: "Johannesburg", country: "ZA", status: "available", lat: -26.2, lon: 28.05 },
  { id: "aicha", name: "Aïcha T.", initials: "AT", role: "QA", stack: ["Playwright", "Cypress", "Postman"], years: 4, photo: `${PORTRAIT_API}/women/30.jpg`, city: "Abidjan", country: "CI", status: "open", lat: 5.36, lon: -4.01 },
  { id: "eric", name: "Eric N.", initials: "EN", role: "Mobile", stack: ["Kotlin", "Compose", "Firebase"], years: 5, photo: `${PORTRAIT_API}/men/91.jpg`, city: "Kigali", country: "RW", status: "available", lat: -1.95, lon: 30.06 },
  { id: "samuel", name: "Samuel B.", initials: "SB", role: "SRE", stack: ["Prometheus", "Go", "Grafana"], years: 7, photo: `${PORTRAIT_API}/men/63.jpg`, city: "Douala", country: "CM", status: "mission", lat: 4.05, lon: 9.7 },
  { id: "fatou", name: "Fatou K.", initials: "FK", role: "Frontend", stack: ["React", "Next.js", "Tailwind"], years: 4, photo: `${PORTRAIT_API}/women/69.jpg`, city: "Bamako", country: "ML", status: "available", lat: 12.64, lon: -8 },
  { id: "baraka", name: "Baraka M.", initials: "BM", role: "AppSec", stack: ["Rust", "OWASP", "Linux"], years: 10, photo: `${PORTRAIT_API}/men/83.jpg`, city: "Dar es Salaam", country: "TZ", status: "open", lat: -6.79, lon: 39.21 },
  { id: "joseph", name: "Joseph O.", initials: "JO", role: "Fullstack", stack: ["Laravel", "Vue", "MySQL"], years: 6, photo: `${PORTRAIT_API}/men/59.jpg`, city: "Kampala", country: "UG", status: "available", lat: 0.35, lon: 32.58 },
  { id: "rodrigue", name: "Rodrigue A.", initials: "RA", role: "Data analyst", stack: ["SQL", "Power BI", "Python"], years: 3, photo: `${PORTRAIT_API}/men/55.jpg`, city: "Cotonou", country: "BJ", status: "mission", lat: 6.37, lon: 2.39 },
];

export const COMPANY_PROFILES: CompanyProfile[] = [
  { id: "sahel-pay", name: "Sahel Pay", initials: "SP", sector: "fintech", teamSize: 40, openRoles: 3, seeking: ["Go", "Django", "React"], city: "Dakar", country: "SN", lat: 14.69, lon: -17.44 },
  { id: "baobab", name: "Baobab Health", initials: "BH", sector: "healthtech", teamSize: 25, openRoles: 2, seeking: ["React", "Node.js", "FHIR"], city: "Abidjan", country: "CI", lat: 5.32, lon: -4.03 },
  { id: "kasa", name: "Kasa Logistics", initials: "KL", sector: "logistics", teamSize: 60, openRoles: 4, seeking: ["Python", "Vue", "PostGIS"], city: "Accra", country: "GH", lat: 5.56, lon: -0.2 },
  { id: "delta", name: "Delta Agritech", initials: "DA", sector: "agritech", teamSize: 30, openRoles: 1, seeking: ["Data", "Python", "IoT"], city: "Kigali", country: "RW", lat: -1.97, lon: 30.1 },
  { id: "nile-learn", name: "Nile Learn", initials: "NL", sector: "edtech", teamSize: 45, openRoles: 2, seeking: ["Flutter", "Django", "UX"], city: "Kampala", country: "UG", lat: 0.31, lon: 32.6 },
  { id: "atlas", name: "Atlas Commerce", initials: "AC", sector: "ecommerce", teamSize: 150, openRoles: 6, seeking: ["Go", "React", "Kafka"], city: "Casablanca", country: "MA", lat: 33.59, lon: -7.62 },
  { id: "savanna", name: "Savanna Energy", initials: "SE", sector: "cleantech", teamSize: 80, openRoles: 3, seeking: ["Rust", "IoT", "Grafana"], city: "Nairobi", country: "KE", lat: -1.31, lon: 36.8 },
  { id: "ubuntu", name: "Ubuntu Cloud", initials: "UC", sector: "saas", teamSize: 35, openRoles: 2, seeking: ["Kubernetes", "Go", "Terraform"], city: "Johannesburg", country: "ZA", lat: -26.17, lon: 28.03 },
  { id: "faso", name: "Faso Connect", initials: "FC", sector: "telecom", teamSize: 300, openRoles: 5, seeking: ["Kotlin", "DevOps", "USSD"], city: "Ouagadougou", country: "BF", lat: 12.35, lon: -1.5 },
  { id: "lagoon", name: "Lagoon Insure", initials: "LI", sector: "insurtech", teamSize: 50, openRoles: 2, seeking: ["Java", "Angular", "SQL"], city: "Lagos", country: "NG", lat: 6.45, lon: 3.4 },
  { id: "medina", name: "Medina Labs", initials: "ML", sector: "ai", teamSize: 20, openRoles: 1, seeking: ["ML", "Python", "Streamlit"], city: "Tunis", country: "TN", lat: 36.82, lon: 10.17 },
  { id: "kivu", name: "Kivu Mobility", initials: "KM", sector: "mobility", teamSize: 70, openRoles: 3, seeking: ["React Native", "Node.js", "Maps"], city: "Lomé", country: "TG", lat: 6.13, lon: 1.22 },
];

const AMBIENT_MARKERS: GlobeMarker[] = [
  { lat: 30.04, lon: 31.24, kind: "company" },
  { lat: 31.2, lon: 29.92, kind: "dev" },
  { lat: 36.75, lon: 3.06, kind: "company" },
  { lat: 35.7, lon: -0.63, kind: "dev" },
  { lat: 34.02, lon: -6.84, kind: "dev" },
  { lat: 31.63, lon: -8, kind: "dev" },
  { lat: 32.89, lon: 13.19, kind: "dev" },
  { lat: 15.5, lon: 32.56, kind: "dev" },
  { lat: 9.03, lon: 38.74, kind: "company" },
  { lat: 11.59, lon: 43.15, kind: "dev" },
  { lat: 2.05, lon: 45.32, kind: "dev" },
  { lat: -18.88, lon: 47.5, kind: "company" },
  { lat: -15.39, lon: 28.32, kind: "dev" },
  { lat: -17.83, lon: 31.05, kind: "dev" },
  { lat: -25.97, lon: 32.57, kind: "dev" },
  { lat: -33.92, lon: 18.42, kind: "company" },
  { lat: -29.86, lon: 31.02, kind: "dev" },
  { lat: -22.56, lon: 17.08, kind: "dev" },
  { lat: -24.65, lon: 25.91, kind: "dev" },
  { lat: -8.84, lon: 13.23, kind: "company" },
  { lat: -4.27, lon: 15.28, kind: "dev" },
  { lat: 0.39, lon: 9.45, kind: "dev" },
  { lat: 3.87, lon: 11.52, kind: "dev" },
  { lat: 12.13, lon: 15.06, kind: "dev" },
  { lat: 13.51, lon: 2.11, kind: "dev" },
  { lat: 18.08, lon: -15.98, kind: "dev" },
  { lat: 9.64, lon: -13.58, kind: "dev" },
  { lat: 8.48, lon: -13.23, kind: "dev" },
  { lat: 6.3, lon: -10.8, kind: "dev" },
  { lat: 9.06, lon: 7.49, kind: "company" },
  { lat: 12, lon: 8.52, kind: "dev" },
  { lat: -20.16, lon: 57.5, kind: "company" },
  { lat: 10.65, lon: -4.76, kind: "dev" },
];

export const GLOBE_MARKERS: GlobeMarker[] = [
  ...DEV_PROFILES.map(({ lat, lon }) => ({ lat, lon, kind: "dev" as const })),
  ...COMPANY_PROFILES.map(({ lat, lon }) => ({ lat, lon, kind: "company" as const })),
  ...AMBIENT_MARKERS,
];

const CONNECTION_PAIRS: [devId: string, companyId: string, event: ConnectionEvent, score?: number][] = [
  ["awa", "baobab", "match", 94],
  ["wendyam", "sahel-pay", "mission"],
  ["tunde", "nile-learn", "match", 91],
  ["grace", "delta", "mission"],
  ["yasmine", "medina", "answer"],
  ["kofi", "ubuntu", "match", 92],
  ["karim", "atlas", "application"],
  ["jean-paul", "savanna", "pr"],
  ["thandiwe", "kasa", "mission"],
  ["aicha", "faso", "application"],
  ["eric", "kivu", "match", 89],
  ["samuel", "lagoon", "pr"],
  ["fatou", "atlas", "answer"],
  ["baraka", "ubuntu", "help"],
  ["joseph", "savanna", "pr"],
  ["rodrigue", "sahel-pay", "match", 90],
];

export const GLOBE_CONNECTIONS: GlobeConnection[] = CONNECTION_PAIRS.flatMap(
  ([devId, companyId, event, score]) => {
    const dev = DEV_PROFILES.find((profile) => profile.id === devId);
    const company = COMPANY_PROFILES.find((profile) => profile.id === companyId);
    return dev && company ? [{ id: `${devId}-${companyId}`, dev, company, event, score }] : [];
  }
);