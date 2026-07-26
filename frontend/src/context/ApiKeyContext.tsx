import { createContext, ReactNode, useContext, useMemo, useState } from "react";

type ApiKeyContextValue = {
  apiKey: string;
  setApiKey: (value: string) => void;
  clearApiKey: () => void;
};

const ApiKeyContext = createContext<ApiKeyContextValue | null>(null);

export function ApiKeyProvider({ children }: { children: ReactNode }) {
  const [apiKey, setApiKey] = useState("");
  const value = useMemo(
    () => ({
      apiKey,
      setApiKey,
      clearApiKey: () => setApiKey("")
    }),
    [apiKey]
  );

  return <ApiKeyContext.Provider value={value}>{children}</ApiKeyContext.Provider>;
}

export function useApiKey() {
  const context = useContext(ApiKeyContext);
  if (!context) {
    throw new Error("useApiKey must be used inside ApiKeyProvider");
  }
  return context;
}
