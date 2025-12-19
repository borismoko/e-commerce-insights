import { BarChart3, TrendingUp, Users, Package, LogOut } from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/contexts/AuthContext";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";

interface SidebarProps {
  activeSection: string;
  onSectionChange: (section: string) => void;
}

const navItems = [
  { id: "overview", label: "Overview", icon: BarChart3 },
  { id: "sales", label: "Sales Prediction", icon: TrendingUp },
  { id: "performance", label: "Product Performance", icon: Package },
  { id: "recommendations", label: "Recommendations", icon: Users },
];

export const Sidebar = ({ activeSection, onSectionChange }: SidebarProps) => {
  const navigate = useNavigate();
  const { logout } = useAuth();

  const handleLogout = () => {
    logout();
    toast.success("Logged out successfully");
    navigate("/auth");
  };

  return (
    <aside className="w-64 bg-sidebar border-r border-sidebar-border flex flex-col">
      <div className="p-6 border-b border-sidebar-border">
        <h1 className="text-xl font-bold text-sidebar-foreground flex items-center gap-2">
          <BarChart3 className="w-6 h-6 text-sidebar-primary" />
          ML Analytics
        </h1>
      </div>
      
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <button
              key={item.id}
              onClick={() => onSectionChange(item.id)}
              className={cn(
                "w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all",
                activeSection === item.id
                  ? "bg-sidebar-accent text-sidebar-primary"
                  : "text-sidebar-foreground hover:bg-sidebar-accent/50"
              )}
            >
              <Icon className="w-5 h-5" />
              {item.label}
            </button>
          );
        })}
      </nav>
      
      <div className="p-4 border-t border-sidebar-border space-y-3">
        <div className="px-4 py-3 rounded-lg bg-sidebar-accent/30">
          <p className="text-xs text-sidebar-foreground/70">ML Model v2.1.0</p>
          <p className="text-xs text-sidebar-foreground/50 mt-1">Last updated: Today</p>
        </div>
        <Button 
          variant="ghost" 
          className="w-full justify-start text-sidebar-foreground hover:bg-sidebar-accent"
          onClick={handleLogout}
        >
          <LogOut className="w-4 h-4 mr-2" />
          Log out
        </Button>
      </div>
    </aside>
  );
};
