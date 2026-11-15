import React, { useState } from "react";
import { useLoginMutation } from "../api";
import { LoginSchema } from "../schema";
import { useTranslation } from "react-i18next";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { CreationSuccessSonner } from "@/helpers/api/feed-backs";
import { FetchBaseQueryError } from "@reduxjs/toolkit/query";

import { Mail, Eye, EyeOff } from "lucide-react";

import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Icons } from "@/lib/constants/icons";
import { renderFetchBaseQueryError } from "@/helpers/api/global-error-catcher";
import { useAuthSlice } from "../slice";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { loginSchema } from "../schema";
import { Link } from "react-router-dom";

const DEV_LOGIN_EMAIL = import.meta.env.DEV
  ? (import.meta.env.VITE_DEV_LOGIN_EMAIL as string | undefined)?.trim() || ""
  : "";
// Nom sans PASSWORD/TOKEN : FE-004 refuse VITE_* secret dans le bundle.
const DEV_LOGIN_PASSWORD = import.meta.env.DEV
  ? (import.meta.env.VITE_DEV_LOGIN_PWD as string | undefined)?.trim() || ""
  : "";

export default function LoginForm() {
  const [login, { isLoading: isSubmitting }] = useLoginMutation();
  const [globalError, setGlobalError] = useState<React.ReactNode>(null);
  const { t } = useTranslation();
  const [showPassword, setShowPassword] = useState(false);
  const loadSession = useAuthSlice((state) => state.loadSession);

  const form = useForm<LoginSchema>({
    resolver: zodResolver(loginSchema(t)),
    defaultValues: {
      email: DEV_LOGIN_EMAIL,
      password: DEV_LOGIN_PASSWORD,
    },
  });

  const onSubmit = async (loginData: LoginSchema) => {
    try {
      setGlobalError(null);
      const loginResponse = await login(loginData).unwrap();
      // Le serveur a posé les cookies de session : on charge le profil et les permissions
      await loadSession();
      form.reset();
      CreationSuccessSonner(
        t("welcome") + " " + loginResponse.user.full_name + " !"
      );
      // La redirection (page d'origine ou accueil) est faite par PublicRoute dès que l'utilisateur est connecté
    } catch (err) {
      const error = err as FetchBaseQueryError;
      if (error.status === 400 && error.data) {
        const errorData = error.data as Record<string, string[]>;
        Object.entries(errorData).forEach(([field, messages]) => {
          if (Array.isArray(messages) && messages.length > 0) {
            form.setError(field as keyof LoginSchema, {
              message: messages[0],
            });
          }
        });
      } else {
        setGlobalError(renderFetchBaseQueryError(error, t));
      }
    }
  };

  return (
    <div className="flex flex-col gap-4">
      {globalError && <div className="mb-4">{globalError}</div>}
      <Form {...form}>
        <form
          className="space-y-6"
          onSubmit={form.handleSubmit(onSubmit)}
          noValidate
        >
          <FormField
            control={form.control}
            name="email"
            render={({ field }) => (
              <FormItem>
                <FormLabel className="text-sm font-medium">
                  {t("email")} *
                </FormLabel>
                <FormControl>
                  <div className="relative">
                    <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input
                      type="email"
                      {...field}
                      placeholder={
                        DEV_LOGIN_EMAIL || "utilisateur@exemple.com"
                      }
                      autoComplete="username"
                      className="pl-10 h-10"
                    />
                  </div>
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="password"
            render={({ field }) => (
              <FormItem>
                <FormLabel className="text-sm font-medium">
                  {t("password")} *
                </FormLabel>
                <FormControl>
                  <div className="relative">
                    <Input
                      type={showPassword ? "text" : "password"}
                      {...field}
                      placeholder={DEV_LOGIN_PASSWORD || "••••••••"}
                      autoComplete="current-password"
                      className="pr-10 h-10"
                    />
                    <Button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      variant="ghost"
                      size="icon"
                      className="absolute right-1 top-1 h-8 w-8 text-muted-foreground hover:text-foreground"
                    >
                      {showPassword ? (
                        <EyeOff className="h-4 w-4" />
                      ) : (
                        <Eye className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <div className="-mt-2 flex justify-end">
            <Link
              to="/forgot-password"
              className="text-sm text-muted-foreground underline-offset-4 hover:text-foreground hover:underline"
            >
              {t("login_form_forgot_password")}
            </Link>
          </div>
          <div className="pt-2">
          <Button type="submit" className="h-10 w-full" disabled={isSubmitting}>
            {isSubmitting ? (
              <>
                <Icons.Loading className="mr-2 h-4 w-4 animate-spin" />
                {t("auth.logging_in")}
              </>
            ) : (
              <>
                <Icons.Login className="mr-2 h-4 w-4" />
                {t("auth.login_title")}
              </>
            )}
          </Button>
        </div>
        </form>
      </Form>
    </div>
  );
}
