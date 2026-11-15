/**
 * Profils de vitrine fictifs et anonymisés : aucun ne correspond à un compte réel.
 */
export type DevStatus = "available" | "mission" | "open";

export type DevProfile = {
  id: string;
  name: string;
  initials: string;
  role: string;
  stack: string[];
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
  sector: string;
  size: string;
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
  event: string;
};

export const DEV_PROFILES: DevProfile[] = [
  { id: "amara", name: "Amara D.", initials: "AD", role: "Backend", stack: ["Django", "PostgreSQL"], city: "Dakar", country: "SN", status: "available", lat: 14.72, lon: -17.45 },
  { id: "lucas", name: "Lucas M.", initials: "LM", role: "Frontend", stack: ["React", "TypeScript"], city: "Lyon", country: "FR", status: "mission", lat: 45.76, lon: 4.84 },
  { id: "priya", name: "Priya S.", initials: "PS", role: "Data engineer", stack: ["Python", "Airflow"], city: "Bangalore", country: "IN", status: "open", lat: 12.97, lon: 77.59 },
  { id: "kenji", name: "Kenji T.", initials: "KT", role: "Mobile", stack: ["Flutter", "Dart"], city: "Osaka", country: "JP", status: "available", lat: 34.69, lon: 135.5 },
  { id: "sofia", name: "Sofía R.", initials: "SR", role: "DevOps", stack: ["Kubernetes", "Helm"], city: "Bogotá", country: "CO", status: "available", lat: 4.71, lon: -74.07 },
  { id: "tunde", name: "Tunde A.", initials: "TA", role: "Fullstack", stack: ["Node.js", "Vue"], city: "Lagos", country: "NG", status: "open", lat: 6.52, lon: 3.38 },
  { id: "elena", name: "Elena V.", initials: "EV", role: "Sécurité", stack: ["Rust", "eBPF"], city: "Varsovie", country: "PL", status: "mission", lat: 52.23, lon: 21.01 },
  { id: "mateus", name: "Mateus C.", initials: "MC", role: "Backend", stack: ["Go", "gRPC"], city: "São Paulo", country: "BR", status: "available", lat: -23.55, lon: -46.63 },
  { id: "leila", name: "Leila B.", initials: "LB", role: "Machine learning", stack: ["PyTorch", "MLOps"], city: "Tunis", country: "TN", status: "open", lat: 36.8, lon: 10.18 },
  { id: "noah", name: "Noah K.", initials: "NK", role: "Cloud", stack: ["AWS", "Terraform"], city: "Toronto", country: "CA", status: "mission", lat: 43.65, lon: -79.38 },
  { id: "minh", name: "Minh N.", initials: "MN", role: "Frontend", stack: ["Vue", "Nuxt"], city: "Hô Chi Minh-Ville", country: "VN", status: "available", lat: 10.82, lon: 106.63 },
  { id: "grace", name: "Grace W.", initials: "GW", role: "Mobile", stack: ["Kotlin", "Compose"], city: "Nairobi", country: "KE", status: "available", lat: -1.29, lon: 36.82 },
  { id: "yasmine", name: "Yasmine E.", initials: "YE", role: "QA", stack: ["Playwright", "Cypress"], city: "Casablanca", country: "MA", status: "open", lat: 33.57, lon: -7.59 },
  { id: "jack", name: "Jack O.", initials: "JO", role: "SRE", stack: ["Prometheus", "Go"], city: "Melbourne", country: "AU", status: "mission", lat: -37.81, lon: 144.96 },
];

export const COMPANY_PROFILES: CompanyProfile[] = [
  { id: "lumen", name: "Lumen Pay", initials: "LP", sector: "Fintech", size: "40 pers.", seeking: ["Go", "Django"], city: "Lisbonne", country: "PT", lat: 38.72, lon: -9.14 },
  { id: "baobab", name: "Baobab Health", initials: "BH", sector: "Santé", size: "25 pers.", seeking: ["React", "Node.js"], city: "Abidjan", country: "CI", lat: 5.36, lon: -4.01 },
  { id: "nordwind", name: "Nordwind Labs", initials: "NL", sector: "Énergie", size: "120 pers.", seeking: ["Rust", "Sécurité"], city: "Berlin", country: "DE", lat: 52.52, lon: 13.4 },
  { id: "kasa", name: "Kasa Logistics", initials: "KL", sector: "Logistique", size: "60 pers.", seeking: ["Python", "Vue"], city: "Accra", country: "GH", lat: 5.6, lon: -0.19 },
  { id: "andes", name: "Andes Cloud", initials: "AC", sector: "SaaS B2B", size: "35 pers.", seeking: ["Kubernetes", "Go"], city: "Santiago", country: "CL", lat: -33.45, lon: -70.67 },
  { id: "sakura", name: "Sakura Mobility", initials: "SM", sector: "Mobilité", size: "200 pers.", seeking: ["Flutter", "Vue"], city: "Tokyo", country: "JP", lat: 35.68, lon: 139.69 },
  { id: "maple", name: "Maple Studio", initials: "MS", sector: "Agence produit", size: "15 pers.", seeking: ["Fullstack", "QA"], city: "Montréal", country: "CA", lat: 45.5, lon: -73.57 },
  { id: "delta", name: "Delta Agritech", initials: "DA", sector: "Agritech", size: "30 pers.", seeking: ["Data", "Python"], city: "Kigali", country: "RW", lat: -1.95, lon: 30.06 },
  { id: "harbor", name: "Harbor Vision", initials: "HV", sector: "IA appliquée", size: "80 pers.", seeking: ["ML", "SRE"], city: "Singapour", country: "SG", lat: 1.35, lon: 103.82 },
  { id: "atlas", name: "Atlas Market", initials: "AM", sector: "E-commerce", size: "150 pers.", seeking: ["Go", "React"], city: "Mexico", country: "MX", lat: 19.43, lon: -99.13 },
  { id: "fjord", name: "Fjord Games", initials: "FG", sector: "Jeu vidéo", size: "45 pers.", seeking: ["C++", "Cloud"], city: "Oslo", country: "NO", lat: 59.91, lon: 10.75 },
  { id: "sahel", name: "Sahel Connect", initials: "SC", sector: "Télécoms", size: "300 pers.", seeking: ["Kotlin", "DevOps"], city: "Bamako", country: "ML", lat: 12.64, lon: -8 },
];

const AMBIENT_MARKERS: GlobeMarker[] = [
  { lat: 48.86, lon: 2.35, kind: "company" },
  { lat: 51.5, lon: -0.12, kind: "company" },
  { lat: 40.71, lon: -74, kind: "company" },
  { lat: 37.77, lon: -122.42, kind: "company" },
  { lat: 25.2, lon: 55.27, kind: "company" },
  { lat: -33.87, lon: 151.21, kind: "company" },
  { lat: 19.08, lon: 72.88, kind: "company" },
  { lat: 22.54, lon: 114.06, kind: "company" },
  { lat: 59.33, lon: 18.07, kind: "company" },
  { lat: 30.04, lon: 31.24, kind: "dev" },
  { lat: -26.2, lon: 28.05, kind: "dev" },
  { lat: 37.57, lon: 126.98, kind: "dev" },
  { lat: -6.2, lon: 106.85, kind: "dev" },
  { lat: 41, lon: 28.98, kind: "dev" },
  { lat: 40.42, lon: -3.7, kind: "dev" },
  { lat: -12.05, lon: -77.04, kind: "dev" },
  { lat: -34.6, lon: -58.38, kind: "dev" },
  { lat: 9.03, lon: 38.74, kind: "dev" },
  { lat: -4.44, lon: 15.27, kind: "dev" },
  { lat: 4.05, lon: 9.7, kind: "dev" },
  { lat: 14.6, lon: 120.98, kind: "dev" },
  { lat: 49.28, lon: -123.12, kind: "dev" },
  { lat: 6.37, lon: 2.39, kind: "dev" },
  { lat: -18.88, lon: 47.5, kind: "dev" },
  { lat: -36.85, lon: 174.76, kind: "dev" },
  { lat: 41.88, lon: -87.63, kind: "dev" },
  { lat: 30.27, lon: -97.74, kind: "dev" },
];

export const GLOBE_MARKERS: GlobeMarker[] = [
  ...DEV_PROFILES.map(({ lat, lon }) => ({ lat, lon, kind: "dev" as const })),
  ...COMPANY_PROFILES.map(({ lat, lon }) => ({ lat, lon, kind: "company" as const })),
  ...AMBIENT_MARKERS,
];

const CONNECTION_PAIRS: [devId: string, companyId: string, event: string][] = [
  ["amara", "lumen", "Match à 94 %"],
  ["tunde", "baobab", "PR fusionnée"],
  ["elena", "nordwind", "Réponse validée"],
  ["leila", "delta", "Mission démarrée"],
  ["grace", "sahel", "Match à 92 %"],
  ["yasmine", "maple", "Candidature retenue"],
  ["sofia", "andes", "Match à 91 %"],
  ["mateus", "atlas", "Mission démarrée"],
  ["noah", "fjord", "PR fusionnée"],
  ["lucas", "kasa", "Réponse validée"],
  ["priya", "harbor", "Mission démarrée"],
  ["minh", "sakura", "Match à 89 %"],
  ["jack", "harbor", "Entraide validée"],
  ["kenji", "maple", "Candidature retenue"],
];

export const GLOBE_CONNECTIONS: GlobeConnection[] = CONNECTION_PAIRS.flatMap(
  ([devId, companyId, event]) => {
    const dev = DEV_PROFILES.find((profile) => profile.id === devId);
    const company = COMPANY_PROFILES.find((profile) => profile.id === companyId);
    return dev && company ? [{ id: `${devId}-${companyId}`, dev, company, event }] : [];
  }
);
