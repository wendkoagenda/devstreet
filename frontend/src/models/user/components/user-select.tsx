import { useState } from "react";
import { RelationSelect } from "@/components/relation-select/relation-select";
import { useGetUsersQuery } from "../api";
import type { GetUserSchema } from "../schema";

type UserSelectProps = {
  value: number | null | undefined;
  onChange: (value: number | null) => void;
  clearable?: boolean;
  disabled?: boolean;
};

const userLabel = (user: GetUserSchema): string => {
  const name = [user.first_name, user.last_name].filter(Boolean).join(" ");
  return name ? `${name} (${user.email})` : user.email || `#${user.id}`;
};

/** Sélecteur d'utilisateur : l'API ne pagine pas /users, le filtre de recherche est donc appliqué côté client. */
export function UserSelect({
  value,
  onChange,
  clearable,
  disabled,
}: UserSelectProps) {
  const [search, setSearch] = useState("");
  const { data, isFetching } = useGetUsersQuery();
  const needle = search.trim().toLowerCase();
  const items = (data ?? []).filter(
    (user) => !needle || userLabel(user).toLowerCase().includes(needle)
  );

  return (
    <RelationSelect<GetUserSchema>
      value={value}
      onChange={onChange}
      items={items}
      getLabel={userLabel}
      onSearchChange={setSearch}
      isLoading={isFetching}
      placeholder="Sélectionner un utilisateur..."
      clearable={clearable}
      disabled={disabled}
    />
  );
}
