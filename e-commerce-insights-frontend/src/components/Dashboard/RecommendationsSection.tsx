import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Users, MapPin, TrendingUp } from "lucide-react";

const demographicInsights = [
  {
    demographic: "Age 25-34, USA",
    categories: ["Electronics", "Sports", "Books"],
    purchaseRate: "High",
    icon: Users,
  },
  {
    demographic: "Age 35-44, UK",
    categories: ["Home & Garden", "Beauty", "Clothing"],
    purchaseRate: "Medium",
    icon: Users,
  },
  {
    demographic: "Age 18-24, Canada",
    categories: ["Clothing", "Electronics", "Beauty"],
    purchaseRate: "High",
    icon: Users,
  },
];

const categoryPairs = [
  { pair: ["Electronics", "Books"], frequency: 847, lift: 2.3 },
  { pair: ["Clothing", "Beauty"], frequency: 692, lift: 2.1 },
  { pair: ["Sports", "Clothing"], frequency: 581, lift: 1.9 },
  { pair: ["Home & Garden", "Electronics"], frequency: 523, lift: 1.7 },
];

export const RecommendationsSection = () => {
  return (
    <div>
      <div className="mb-6">
        <h2 className="text-3xl font-bold text-foreground">Product Recommendations</h2>
        <p className="text-muted-foreground mt-1">Collaborative filtering insights</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="w-5 h-5 text-primary" />
              Top Categories by Demographics
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {demographicInsights.map((insight, idx) => {
                const Icon = insight.icon;
                return (
                  <div key={idx} className="p-4 rounded-lg bg-muted/50">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <Icon className="w-4 h-4 text-primary" />
                        <p className="font-medium text-foreground">{insight.demographic}</p>
                      </div>
                      <Badge variant={insight.purchaseRate === "High" ? "default" : "secondary"}>
                        {insight.purchaseRate}
                      </Badge>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {insight.categories.map((cat, i) => (
                        <Badge key={i} variant="outline" className="text-xs">
                          #{i + 1} {cat}
                        </Badge>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-primary" />
              Frequently Bought Together
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {categoryPairs.map((item, idx) => (
                <div key={idx} className="p-4 rounded-lg bg-muted/50">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline">{item.pair[0]}</Badge>
                      <span className="text-muted-foreground">+</span>
                      <Badge variant="outline">{item.pair[1]}</Badge>
                    </div>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <p className="text-muted-foreground">{item.frequency} co-purchases</p>
                    <Badge className="bg-success text-success-foreground">
                      {item.lift}x lift
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MapPin className="w-5 h-5 text-primary" />
            Geographic Purchase Patterns
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 rounded-lg bg-muted/50">
              <p className="text-2xl font-bold text-foreground mb-1">USA</p>
              <p className="text-sm text-muted-foreground mb-3">Most popular: Electronics</p>
              <div className="flex gap-2">
                <Badge variant="outline" className="text-xs">Tech Savvy</Badge>
                <Badge variant="outline" className="text-xs">High Spending</Badge>
              </div>
            </div>
            <div className="p-4 rounded-lg bg-muted/50">
              <p className="text-2xl font-bold text-foreground mb-1">UK</p>
              <p className="text-sm text-muted-foreground mb-3">Most popular: Home & Garden</p>
              <div className="flex gap-2">
                <Badge variant="outline" className="text-xs">Quality Focus</Badge>
                <Badge variant="outline" className="text-xs">Premium</Badge>
              </div>
            </div>
            <div className="p-4 rounded-lg bg-muted/50">
              <p className="text-2xl font-bold text-foreground mb-1">Canada</p>
              <p className="text-sm text-muted-foreground mb-3">Most popular: Clothing</p>
              <div className="flex gap-2">
                <Badge variant="outline" className="text-xs">Fashion Forward</Badge>
                <Badge variant="outline" className="text-xs">Eco-conscious</Badge>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
