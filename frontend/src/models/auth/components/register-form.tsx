import React, { useState } from "react";
import { useRegisterMutation } from "../api";
import { RegisterSchema, registerSchema } from "../schema";
import { useTranslation } from "react-i18next";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { CreationSuccessSonner } from "@/helpers/api/feed-backs";
import { FetchBaseQueryError } from "@reduxjs/toolkit/query";
import { Eye, EyeOff, Mail, User } from "lucide-react";
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

export default function RegisterForm() {
  const [register, { isLoading: isSubmitting }] = useRegisterMutation();
  const [globalError, setGlobalError] = useState<React.ReactNode>(null);
  const { t } = useTranslation();
  const [showPassword, setShowPassword] = useState(false);
  const loadSession = useAuthSlice((state) => state.loadSession);

  const form = useForm<RegisterSchema>({
    resolver: zodResolver(registerSchema(t)),
    defaultValues: {
      first_name: "",
      last_name: "",
      username: "",
      email: "",
      password: "",
      password_confirm: "",
    },
  });

  const onSubmit = async (data: RegisterSchema) => {
    try {
      setGlobalError(null);
      const response = await register({
        ...data,
        username: data.username.trim(),
      }).unwrap();
      await loadSession();
      form.reset();
      CreationSuccessSonner(
        t("welcome") + " " + response.user.full_name + " !"
      );
    } catch (err) {
      const error = err as FetchBaseQueryError;
      if ((error.status === 400 || error.status === 401) && error.data) {
        const errorData = error.data as Record<string, string[] | string>;
        Object.entries(errorData).forEach(([field, messages]) => {
          const message = Array.isArray(messages) ? messages[0] : messages;
          if (
            message &&
            [
              "email",
              "username",
              "first_name",
              "last_name",
              "password",
              "password_confirm",
            ].includes(field)
          ) {
            form.setError(field as keyof RegisterSchema, { message });
          }
        });
        if (typeof errorData.detail === "string") {
          setGlobalError(errorData.detail);
        }
      } else {
        setGlobalError(renderFetchBaseQueryError(error, t));
      }
    }
  };

  return (
    <div className="flex flex-col gap-3">
      {globalError && <div className="mb-2 text-sm text-destructive">{globalError}</div>}
      <Form {...form}>
        <form
          className="space-y-3"
          onSubmit={form.handleSubmit(onSubmit)}
          noValidate
        >
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <FormField
              control={form.control}
              name="first_name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-sm font-medium">
                    {t("first_name")} *
                  </FormLabel>
                  <FormControl>
                    <Input {...field} className="h-10" autoComplete="given-name" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="last_name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-sm font-medium">
                    {t("last_name")} *
                  </FormLabel>
                  <FormControl>
                    <Input {...field} className="h-10" autoComplete="family-name" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>

          <FormField
            control={form.control}
            name="username"
            render={({ field }) => (
              <FormItem>
                <FormLabel className="text-sm font-medium">
                  {t("username")} *
                </FormLabel>
                <FormControl>
                  <div className="relative">
                    <User className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input
                      {...field}
                      placeholder={t("auth.username_placeholder")}
                      className="h-10 pl-10"
                      autoComplete="username"
                    />
                  </div>
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

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
                      placeholder="utilisateur@exemple.com"
                      className="h-10 pl-10"
                      autoComplete="email"
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
                      placeholder="••••••••"
                      className="h-10 pr-10"
                      autoComplete="new-password"
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

          <FormField
            control={form.control}
            name="password_confirm"
            render={({ field }) => (
              <FormItem>
                <FormLabel className="text-sm font-medium">
                  {t("password_confirm")} *
                </FormLabel>
                <FormControl>
                  <Input
                    type={showPassword ? "text" : "password"}
                    {...field}
                    placeholder="••••••••"
                    className="h-10"
                    autoComplete="new-password"
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <div className="pt-1">
            <Button type="submit" className="h-10 w-full" disabled={isSubmitting}>
              {isSubmitting ? (
                <>
                  <Icons.Loading className="mr-2 h-4 w-4 animate-spin" />
                  {t("auth.registering")}
                </>
              ) : (
                t("auth.register_submit")
              )}
            </Button>
          </div>
        </form>
      </Form>
    </div>
  );
}
