export function generateBreadcrumbs(
  currentPath: string,
  breadcrumbTitles: Record<string, string>
) {
  const pathSegments = currentPath.split("/").filter(Boolean); // Diviser l'URL en segments
  const breadcrumbs: { url: string; title: string; isLast: boolean }[] = [];

  let accumulatedPath = "";

  pathSegments.forEach((segment, index) => {
    accumulatedPath += `/${segment}`;

    // Chercher une correspondance exacte ou dynamique
    const matchedPath =
      Object.keys(breadcrumbTitles).find((key) => {
        const dynamicPattern = key.replace(/\*/g, "([^/]+)");
        const regex = new RegExp(`^${dynamicPattern}$`);
        return regex.test(accumulatedPath);
      }) || accumulatedPath;

    // Si l'URL correspond exactement à une clé dans `breadcrumbTitles`, utilisez ce titre
    if (breadcrumbTitles[matchedPath]) {
      breadcrumbs.push({
        url: accumulatedPath,
        title: breadcrumbTitles[matchedPath],
        isLast: index === pathSegments.length - 1,
      });
    }
  });

  return breadcrumbs;
}
