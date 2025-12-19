import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp, TrendingDown, DollarSign, ShoppingCart, Users } from "lucide-react";
import { dashboardApi, DashboardMetrics } from "@/lib/api";

const metricConfig = [
  {
    title: "Total Revenue",
    key: "total_revenue" as keyof DashboardMetrics,
    icon: DollarSign,
    color: "text-chart-1",
    formatValue: (val: number) => `$${val.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
  },
  {
    title: "Total Orders",
    key: "total_orders" as keyof DashboardMetrics,
    icon: ShoppingCart,
    color: "text-chart-2",
    formatValue: (val: number) => val.toLocaleString(),
  },
  {
    title: "Active Users",
    key: "active_users" as keyof DashboardMetrics,
    icon: Users,
    color: "text-chart-3",
    formatValue: (val: number) => val.toLocaleString(),
  },
  {
    title: "Avg. Order Value",
    key: "avg_order_value" as keyof DashboardMetrics,
    icon: TrendingUp,
    color: "text-chart-4",
    formatValue: (val: number) => `$${val.toFixed(2)}`,
  },
];

export const OverviewSection = () => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setLoading(true);
        const data = await dashboardApi.getMetrics();
        setMetrics(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load metrics");
        console.error("Error fetching metrics:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
  }, []);

  if (loading) {
    return (
      <div>
        <div className="mb-6">
          <h2 className="text-3xl font-bold text-foreground">Dashboard Overview</h2>
          <p className="text-muted-foreground mt-1">Real-time insights from your ML models</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {metricConfig.map((config) => (
            <Card key={config.title} className="animate-pulse">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {config.title}
                </CardTitle>
                <div className="w-5 h-5 bg-muted rounded" />
              </CardHeader>
              <CardContent>
                <div className="h-8 bg-muted rounded mb-2" />
                <div className="h-4 bg-muted rounded w-24" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (error || !metrics) {
    return (
      <div>
        <div className="mb-6">
          <h2 className="text-3xl font-bold text-foreground">Dashboard Overview</h2>
          <p className="text-muted-foreground mt-1">Real-time insights from your ML models</p>
        </div>
        <Card>
          <CardContent className="p-6">
            <p className="text-destructive">{error || "Failed to load metrics"}</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-3xl font-bold text-foreground">Dashboard Overview</h2>
        <p className="text-muted-foreground mt-1">Real-time insights from your ML models</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metricConfig.map((config) => {
          const Icon = config.icon;
          const metricData = metrics[config.key];
          const value = metricData?.value ?? 0;
          const growth = metricData?.growth ?? 0;
          const isPositive = growth >= 0;
          
          return (
            <Card key={config.title} className="hover:shadow-lg transition-shadow">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {config.title}
                </CardTitle>
                <Icon className={`w-5 h-5 ${config.color}`} />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-foreground">
                  {config.formatValue(value)}
                </div>
                <p className={`text-xs flex items-center gap-1 mt-1 ${isPositive ? 'text-success' : 'text-destructive'}`}>
                  {isPositive ? (
                    <TrendingUp className="w-3 h-3" />
                  ) : (
                    <TrendingDown className="w-3 h-3" />
                  )}
                  {isPositive ? '+' : ''}{growth.toFixed(1)}% from last month
                </p>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
};
