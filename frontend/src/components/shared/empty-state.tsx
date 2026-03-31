import { LucideIcon } from "lucide-react";

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description: string;
  action?: React.ReactNode;
}

export function EmptyState({ icon: Icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center rounded-xl border border-white/[0.06] bg-white/[0.02] p-12 text-center">
      <Icon className="size-12 text-zinc-600 mb-4" />
      <h3 className="text-lg font-semibold">{title}</h3>
      <p className="text-sm text-zinc-500 mt-2 mb-6 max-w-sm leading-relaxed">
        {description}
      </p>
      {action}
    </div>
  );
}
