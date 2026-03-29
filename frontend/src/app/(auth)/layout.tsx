export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      <div className="w-full max-w-sm space-y-8">
        <div className="text-center space-y-2">
          <div className="inline-flex items-center justify-center size-10 rounded-lg bg-primary/10 mb-2">
            <span className="text-lg font-bold text-primary">K</span>
          </div>
          <h1 className="text-2xl font-semibold tracking-tight">Kairos</h1>
          <p className="text-sm text-muted-foreground">
            Portal de clientes para freelancers
          </p>
        </div>
        {children}
      </div>
    </div>
  );
}
