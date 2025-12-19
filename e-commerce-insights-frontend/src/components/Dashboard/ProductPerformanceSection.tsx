import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { TrendingUp, TrendingDown } from "lucide-react";
import { dashboardApi, CategoryPerformance } from "@/lib/api";

export const ProductPerformanceSection = () => {
  const [categoryData, setCategoryData] = useState<CategoryPerformance[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        setLoading(true);
        const data = await dashboardApi.getCategories();
        setCategoryData(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load category data");
        console.error("Error fetching categories:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchCategories();
  }, []);

  if (loading) {
    return (
      <div>
        <div className="mb-6">
          <h2 className="text-3xl font-bold text-foreground">Product Performance</h2>
          <p className="text-muted-foreground mt-1">Category analysis and revenue trends</p>
        </div>
        <Card className="mb-6 animate-pulse">
          <CardHeader>
            <CardTitle>Revenue by Category</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] bg-muted rounded" />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Category Rankings</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="h-16 bg-muted rounded" />
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error || categoryData.length === 0) {
    return (
      <div>
        <div className="mb-6">
          <h2 className="text-3xl font-bold text-foreground">Product Performance</h2>
          <p className="text-muted-foreground mt-1">Category analysis and revenue trends</p>
        </div>
        <Card>
          <CardContent className="p-6">
            <p className="text-destructive">
              {error || "No category data available"}
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-3xl font-bold text-foreground">Product Performance</h2>
        <p className="text-muted-foreground mt-1">Category analysis and revenue trends</p>
      </div>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Revenue by Category</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={categoryData}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="name" stroke="hsl(var(--muted-foreground))" />
              <YAxis stroke="hsl(var(--muted-foreground))" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "var(--radius)"
                }}
                formatter={(value: number) => `$${value.toLocaleString()}`}
              />
              <Bar dataKey="revenue" fill="hsl(var(--chart-1))" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Category Rankings</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {categoryData.map((category) => (
              <div key={category.name} className="flex items-center justify-between p-4 rounded-lg bg-muted/50">
                <div className="flex items-center gap-4">
                  <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary text-primary-foreground font-bold text-sm">
                    {category.rank}
                  </div>
                  <div>
                    <p className="font-medium text-foreground">{category.name}</p>
                    <p className="text-sm text-muted-foreground">
                      ${(category.revenue / 1000).toFixed(0)}K revenue
                    </p>
                  </div>
                </div>
                <Badge 
                  variant={category.growth > 0 ? "default" : "destructive"}
                  className="flex items-center gap-1"
                >
                  {category.growth > 0 ? (
                    <TrendingUp className="w-3 h-3" />
                  ) : (
                    <TrendingDown className="w-3 h-3" />
                  )}
                  {Math.abs(category.growth).toFixed(1)}%
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
