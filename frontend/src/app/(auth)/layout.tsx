export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-[#09090b] bg-[radial-gradient(ellipse_at_center,rgba(74,222,128,0.03),transparent_70%)] p-4">
      <div className="w-full max-w-sm space-y-8">
        <div className="text-center space-y-2">
          <div className="inline-flex items-center justify-center size-12 rounded-lg bg-green-500/10 border border-green-500/20 mb-3">
            <span className="text-xl font-bold text-green-400">K</span>
          </div>
          <h1 className="text-3xl font-bold tracking-tighter">Kairos</h1>
          <p className="text-sm text-zinc-500">
            Portal de clientes para freelancers
          </p>
        </div>
        {children}
      </div>
    </div>
  );
}
