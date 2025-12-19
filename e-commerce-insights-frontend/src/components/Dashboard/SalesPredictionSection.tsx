import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp, TrendingDown, Calendar } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { dashboardApi, ForecastPeriod, BiweeklySalesBucket } from "@/lib/api";

export const SalesPredictionSection = () => {
  const [predictions, setPredictions] = useState<ForecastPeriod[]>([]);
  const [biweeklySales, setBiweeklySales] = useState<BiweeklySalesBucket[]>([]);
  const [biweeklyForecasts, setBiweeklyForecasts] = useState<BiweeklySalesBucket[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [forecastsData, biweekly, biweeklyPredicted] = await Promise.all([
          dashboardApi.getForecasts(),
          dashboardApi.getBiweeklySales(),
          dashboardApi.getBiweeklyForecasts(),
        ]);
        setPredictions(forecastsData.periods);
        setBiweeklySales(biweekly);
        setBiweeklyForecasts(biweeklyPredicted);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load prediction data");
        console.error("Error fetching predictions:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Prepare chart data combining actual and predicted biweekly sales
  // Combine actual and predicted data
  // Start with actual sales, then add predicted for future periods
  const chartData = [
    // Historical actual sales
    ...biweeklySales.map((b) => ({
      name: b.label,
      actual: b.revenue,
      predicted: null as number | null,
      start: b.start,
      end: b.end,
    })),
    // Future predicted sales
    ...biweeklyForecasts.map((b) => ({
      name: b.label,
      actual: null as number | null,
      predicted: b.revenue,
      start: b.start,
      end: b.end,
    })),
  ].sort((a, b) => {
    // Sort by start date to ensure chronological order
    return new Date(a.start).getTime() - new Date(b.start).getTime();
  });

  if (loading) {
    return (
      <div>
        <div className="mb-6">
          <h2 className="text-3xl font-bold text-foreground">Sales Prediction</h2>
          <p className="text-muted-foreground mt-1">AI-powered revenue forecasting</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-4 bg-muted rounded w-20 mb-2" />
              </CardHeader>
              <CardContent>
                <div className="h-8 bg-muted rounded mb-2" />
                <div className="h-4 bg-muted rounded w-32" />
              </CardContent>
            </Card>
          ))}
        </div>
        <Card className="animate-pulse">
          <CardHeader>
            <CardTitle>Sales Trend & Forecast</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] bg-muted rounded" />
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div>
        <div className="mb-6">
          <h2 className="text-3xl font-bold text-foreground">Sales Prediction</h2>
          <p className="text-muted-foreground mt-1">AI-powered revenue forecasting</p>
        </div>
        <Card>
          <CardContent className="p-6">
            <p className="text-destructive">{error}</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-3xl font-bold text-foreground">Sales Prediction</h2>
        <p className="text-muted-foreground mt-1">AI-powered revenue forecasting</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        {predictions.map((pred) => {
          const isPositive = pred.change >= 0;
          return (
            <Card key={pred.period} className="hover:shadow-lg transition-shadow">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {pred.period}
                </CardTitle>
                <Calendar className="w-5 h-5 text-primary" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-foreground">
                  ${pred.value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </div>
                <div className="flex items-center justify-between mt-2">
                  <p className={`text-xs flex items-center gap-1 ${isPositive ? 'text-success' : 'text-destructive'}`}>
                    {isPositive ? (
                      <TrendingUp className="w-3 h-3" />
                    ) : (
                      <TrendingDown className="w-3 h-3" />
                    )}
                    {isPositive ? '+' : ''}{pred.change.toFixed(1)}%
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {pred.confidence.toFixed(0)}% confidence
                  </p>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Sales Trend & Forecast (Biweekly, Last 6 Months)</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="name" stroke="hsl(var(--muted-foreground))" />
              <YAxis stroke="hsl(var(--muted-foreground))" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "var(--radius)"
                }}
                formatter={(value: number | null) => {
                  if (value === null || value === undefined) return "N/A";
                  return `$${value.toLocaleString()}`;
                }}
              />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="actual" 
                stroke="hsl(var(--primary))" 
                strokeWidth={2}
                dot={{ fill: "hsl(var(--primary))" }}
                name="Actual Sales"
                connectNulls={false}
              />
              <Line 
                type="monotone" 
                dataKey="predicted" 
                stroke="hsl(var(--muted-foreground))" 
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={{ fill: "hsl(var(--muted-foreground))", r: 3 }}
                name="Predicted Sales"
                connectNulls={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
};
