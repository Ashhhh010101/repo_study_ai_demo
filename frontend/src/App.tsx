import Home from "./pages/Home";
import RepoReport from "./pages/RepoReport";
import { ApiKeyProvider } from "./context/ApiKeyContext";
import { RouterProvider, useRouter } from "./context/RouterContext";

function AppRoutes() {
  const { path } = useRouter();
  const projectMatch = path.match(/^\/projects\/(\d+)\/?$/);

  if (projectMatch) {
    return <RepoReport projectId={projectMatch[1]} />;
  }
  return <Home />;
}

export default function App() {
  return (
    <ApiKeyProvider>
      <RouterProvider>
        <AppRoutes />
      </RouterProvider>
    </ApiKeyProvider>
  );
}
