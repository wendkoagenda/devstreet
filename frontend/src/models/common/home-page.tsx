import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Users,
  Shield,
  Home,
  Settings,
  TrendingUp,
  Activity,
} from "lucide-react";
import { useTranslation } from "react-i18next";
import { useAuthSlice } from "../auth/slice";
import { usePermissions } from "@/hooks/use-permissions";

export default function HomePage() {
  const { t } = useTranslation();
  const { user } = useAuthSlice();
  const { canViewUsers, canViewRoles } = usePermissions();

  const quickActions = [
    {
      title: t("users.name"),
      description: t("users.description"),
      icon: Users,
      path: "/users",
      show: canViewUsers,
    },
    {
      title: t("roles.name"),
      description: t("roles.description"),
      icon: Shield,
      path: "/roles",
      show: canViewRoles,
    },
  ];

  const stats = [
    {
      title: "Utilisateurs actifs",
      value: "128",
      change: "+12%",
      icon: Users,
      color: "text-chart-1",
    },
    {
      title: "Rôles configurés",
      value: "8",
      change: "+2",
      icon: Shield,
      color: "text-chart-2",
    },
    {
      title: "Sessions actives",
      value: "24",
      change: "+5%",
      icon: Activity,
      color: "text-chart-3",
    },
    {
      title: "Temps de réponse",
      value: "145ms",
      change: "-8%",
      icon: TrendingUp,
      color: "text-chart-5",
    },
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Header de bienvenue */}
      <div className="bg-primary text-primary-foreground">
        <div className="container mx-auto px-6 py-12">
          <div className="flex items-center gap-4 mb-4">
            <div className="p-3 bg-primary-foreground/20 rounded-full">
              <Home className="h-8 w-8" />
            </div>
            <div>
              <h1 className="text-4xl font-bold">
                {t("welcome")} {user?.full_name || user?.username} ! 👋
              </h1>
              <p className="text-xl text-primary-foreground/80 mt-2">
                Bienvenue sur votre espace de gestion OnePourcent
              </p>
            </div>
          </div>
          <p className="text-lg text-primary-foreground/80 max-w-2xl">
            Gérez vos utilisateurs, rôles et permissions en toute simplicité.
            Votre tableau de bord vous donne un aperçu complet de votre système.
          </p>
        </div>
      </div>

      <div className="container mx-auto px-6 py-8">
        {/* Statistiques */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, index) => (
            <Card key={index} className="hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">
                      {stat.title}
                    </p>
                    <p className="text-3xl font-bold">{stat.value}</p>
                    <p
                      className={`text-sm ${
                        stat.change.startsWith("+")
                          ? "text-success"
                          : "text-destructive"
                      }`}
                    >
                      {stat.change} ce mois
                    </p>
                  </div>
                  <div className={`p-3 rounded-full bg-muted ${stat.color}`}>
                    <stat.icon className="h-6 w-6" />
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Actions rapides */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                Actions rapides
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {quickActions
                .filter((action) => action.show)
                .map((action, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-full bg-primary text-primary-foreground">
                        <action.icon className="h-4 w-4" />
                      </div>
                      <div>
                        <h3 className="font-medium">{action.title}</h3>
                        <p className="text-sm text-muted-foreground">
                          {action.description}
                        </p>
                      </div>
                    </div>
                    <Button variant="outline" size="sm">
                      Gérer
                    </Button>
                  </div>
                ))}

              {quickActions.filter((action) => action.show).length === 0 && (
                <div className="text-center py-8 text-muted-foreground">
                  <Shield className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>Aucune action disponible avec vos permissions actuelles</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Informations système */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5" />
                Informations système
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-muted/50 rounded-lg">
                  <h4 className="font-medium text-sm">Version</h4>
                  <p className="text-lg font-bold">v{t("app.version")}</p>
                </div>
                <div className="p-4 bg-muted/50 rounded-lg">
                  <h4 className="font-medium text-sm">Statut</h4>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-success rounded-full"></div>
                    <span className="text-sm font-medium">En ligne</span>
                  </div>
                </div>
              </div>

              <div className="p-4 border rounded-lg">
                <h4 className="font-medium mb-2">Votre profil</h4>
                <div className="space-y-2 text-sm">
                  <p>
                    <span className="font-medium">Email:</span> {user?.email}
                  </p>
                  <p>
                    <span className="font-medium">Rôles:</span>{" "}
                    {user?.roles?.join(", ") || "Aucun"}
                  </p>
                  <p>
                    <span className="font-medium">Dernière connexion:</span>{" "}
                    Maintenant
                  </p>
                </div>
              </div>

              <div className="pt-4">
                <Button className="w-full" variant="outline">
                  <Settings className="h-4 w-4 mr-2" />
                  Paramètres du compte
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Footer */}
        <div className="mt-12 text-center text-muted-foreground">
          <p className="text-sm">
            © {new Date().getFullYear()} OnePourcent devstreet - Développé avec ❤️
          </p>
        </div>
      </div>
    </div>
  );
}
