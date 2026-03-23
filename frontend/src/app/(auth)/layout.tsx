export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-muted/40 p-4">
      <div className="w-full max-w-md space-y-6">
        <div className="text-center">
          <h1 className="text-3xl font-bold tracking-tight">Kairos</h1>
          <p className="text-muted-foreground mt-1">
            Portal de clientes para freelancers
          </p>
        </div>
        {children}
      </div>
    </div>
  );
}
