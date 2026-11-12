export type DjangoValidationError = {
  status: number;
  data: Record<string, string[]>;
};
