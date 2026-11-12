import { buildFilePath } from "@/helpers/displayers/file-name-builder";

type FileFieldDescriptor = {
  name: string;
  uploadFolder: string;
};

type BuildModelFormDataOptions = {
  fileFields: FileFieldDescriptor[];
  fileValues?: Record<string, File | null | undefined>;
};

function appendScalar(formData: FormData, key: string, value: unknown) {
  if (value === undefined) {
    return;
  }
  if (value === null) {
    formData.append(key, "");
    return;
  }
  if (typeof value === "boolean") {
    formData.append(key, value ? "true" : "false");
    return;
  }
  formData.append(key, String(value));
}

export function buildModelFormData(
  payload: Record<string, unknown>,
  options: BuildModelFormDataOptions,
): FormData {
  const formData = new FormData();
  const fileFieldNames = new Set(options.fileFields.map((field) => field.name));

  Object.entries(payload).forEach(([key, value]) => {
    if (fileFieldNames.has(key)) {
      return;
    }
    appendScalar(formData, key, value);
  });

  options.fileFields.forEach((field) => {
    const file = options.fileValues?.[field.name];
    if (!file) {
      return;
    }
    const relativePath = buildFilePath(field.uploadFolder, file.name, true);
    formData.append(field.name, file);
    formData.append(`${field.name}_path`, relativePath);
  });

  return formData;
}

export function hasFilePayload(
  fileFields: FileFieldDescriptor[],
  fileValues?: Record<string, File | null | undefined>,
): boolean {
  return fileFields.some((field) => Boolean(fileValues?.[field.name]));
}
