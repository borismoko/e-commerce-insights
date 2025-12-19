import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Sidebar } from "@/components/Layout/Sidebar";
import { OverviewSection } from "@/components/Dashboard/OverviewSection";
import { SalesPredictionSection } from "@/components/Dashboard/SalesPredictionSection";
import { ProductPerformanceSection } from "@/components/Dashboard/ProductPerformanceSection";
import { RecommendationsSection } from "@/components/Dashboard/RecommendationsSection";
import { AuthGuard } from "@/components/Layout/AuthGuard";
import { uploadApi } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";

const Index = () => {
  const [activeSection, setActiveSection] = useState("overview");
  const [isCheckingFiles, setIsCheckingFiles] = useState(true);
  const navigate = useNavigate();
  const { isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    const checkForFiles = async () => {
      if (!isAuthenticated || isLoading) return;

      try {
        const files = await uploadApi.getFiles();
        if (files.length === 0) {
          navigate("/no-data");
          return;
        }
      } catch (error) {
        console.error("Error checking for files:", error);
        // If there's an error, still show the dashboard (don't block user)
      } finally {
        setIsCheckingFiles(false);
      }
    };

    checkForFiles();
  }, [isAuthenticated, isLoading, navigate]);

  const renderSection = () => {
    switch (activeSection) {
      case "overview":
        return <OverviewSection />;
      case "sales":
        return <SalesPredictionSection />;
      case "performance":
        return <ProductPerformanceSection />;
      case "recommendations":
        return <RecommendationsSection />;
      default:
        return <OverviewSection />;
    }
  };

  if (isCheckingFiles || isLoading) {
    return (
      <AuthGuard>
        <div className="flex min-h-screen items-center justify-center bg-background">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading...</p>
          </div>
        </div>
      </AuthGuard>
    );
  }

  return (
    <AuthGuard>
      <div className="flex min-h-screen bg-background">
        <Sidebar activeSection={activeSection} onSectionChange={setActiveSection} />
        <main className="flex-1 p-8 overflow-y-auto">
          {renderSection()}
        </main>
      </div>
    </AuthGuard>
  );
};

export default Index;
