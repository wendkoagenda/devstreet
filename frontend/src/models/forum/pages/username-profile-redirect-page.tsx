import { Navigate, useParams } from "react-router-dom";
import { profilePath } from "@/helpers/routes/profile-path";

/** Ancienne adresse /forum/u/:username → /profil/:username */
export default function UsernameProfileRedirectPage() {
  const { username = "" } = useParams<{ username: string }>();
  if (!username.trim()) {
    return (
      <p className="py-16 text-center text-sm text-muted-foreground">
        Profil introuvable.
      </p>
    );
  }
  return <Navigate to={profilePath(username.trim())} replace />;
}
