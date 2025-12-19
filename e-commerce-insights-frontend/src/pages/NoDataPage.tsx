import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Upload, FileText, AlertCircle, CheckCircle2, Loader2, ArrowLeft } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { uploadApi } from "@/lib/api";
import { useNavigate } from "react-router-dom";
import { toast } from "@/hooks/use-toast";
import { AuthGuard } from "@/components/Layout/AuthGuard";

const NoDataPage = () => {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<"idle" | "success" | "error">("idle");
  const [isCheckingFiles, setIsCheckingFiles] = useState(true);
  const { checkAuth, isAuthenticated, isLoading } = useAuth();
  const navigate = useNavigate();

  // Check if user already has files when component mounts
  useEffect(() => {
    const checkForFiles = async () => {
      if (!isAuthenticated || isLoading) return;

      try {
        const files = await uploadApi.getFiles();
        if (files.length > 0) {
          navigate("/");
          return;
        }
      } catch (error) {
        console.error("Error checking for files:", error);
      } finally {
        setIsCheckingFiles(false);
      }
    };

    checkForFiles();
  }, [isAuthenticated, isLoading, navigate]);

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.name.endsWith(".csv")) {
      toast({
        title: "Invalid file type",
        description: "Please upload a CSV file.",
        variant: "destructive",
      });
      return;
    }

    // Validate file size (10MB)
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
      toast({
        title: "File too large",
        description: "File size must be less than 10MB.",
        variant: "destructive",
      });
      return;
    }

    setIsUploading(true);
    setUploadStatus("idle");

    try {
      await uploadApi.uploadCsv(file, 30);
      setUploadStatus("success");
      toast({
        title: "Upload successful",
        description: "Your CSV file has been uploaded and processed successfully.",
      });
      
      // Refresh auth to get updated user state
      await checkAuth();
      
      // Redirect to dashboard after a short delay
      setTimeout(() => {
        navigate("/");
      }, 2000);
    } catch (error) {
      setUploadStatus("error");
      toast({
        title: "Upload failed",
        description: error instanceof Error ? error.message : "Failed to upload file. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsUploading(false);
      // Reset file input
      event.target.value = "";
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
      <div className="min-h-screen bg-background flex items-center justify-center p-4 relative">
        <Button
          variant="ghost"
          size="icon"
          className="absolute top-4 left-4"
          onClick={() => navigate("/auth")}
        >
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <Card className="w-full max-w-2xl">
          <CardHeader className="text-center">
            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-muted">
              <FileText className="h-8 w-8 text-muted-foreground" />
            </div>
            <CardTitle className="text-3xl">No Data Uploaded</CardTitle>
            <CardDescription className="text-lg mt-2">
              To get started with e-commerce insights, please upload your sales data CSV file.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Upload Section */}
            <div className="space-y-4">
              <div className="flex items-center justify-center">
                <label htmlFor="csv-upload">
                  <input
                    id="csv-upload"
                    type="file"
                    accept=".csv"
                    onChange={handleFileSelect}
                    disabled={isUploading}
                    className="hidden"
                  />
                  <Button
                    size="lg"
                    disabled={isUploading}
                    className="w-full sm:w-auto"
                    asChild
                  >
                    <span>
                      {isUploading ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Uploading and processing...
                        </>
                      ) : (
                        <>
                          <Upload className="mr-2 h-4 w-4" />
                          Upload CSV File
                        </>
                      )}
                    </span>
                  </Button>
                </label>
              </div>

              {/* Upload Status */}
              {uploadStatus === "success" && (
                <div className="flex items-center justify-center gap-2 text-success">
                  <CheckCircle2 className="h-5 w-5" />
                  <p className="text-sm font-medium">File uploaded successfully! Redirecting...</p>
                </div>
              )}

              {uploadStatus === "error" && (
                <div className="flex items-center justify-center gap-2 text-destructive">
                  <AlertCircle className="h-5 w-5" />
                  <p className="text-sm font-medium">Upload failed. Please try again.</p>
                </div>
              )}
            </div>

            {/* Instructions */}
            <div className="border-t pt-6 space-y-4">
              <h3 className="font-semibold text-lg">File Requirements:</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex items-start gap-2">
                  <span className="text-primary">•</span>
                  <span>File format: CSV (Comma-separated values)</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary">•</span>
                  <span>Maximum file size: 10MB</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary">•</span>
                  <span>
                    Required columns: transaction_id, user_name, age, country, product_category,
                    purchase_amount, payment_method, transaction_date
                  </span>
                </li>
              </ul>
            </div>

            {/* Expected Format */}
            <div className="border-t pt-6">
              <h3 className="font-semibold text-lg mb-3">Expected CSV Format:</h3>
              <div className="bg-muted p-4 rounded-md overflow-x-auto">
                <code className="text-xs">
                  <div>transaction_id,user_name,age,country,product_category,purchase_amount,payment_method,transaction_date</div>
                  <div className="text-muted-foreground mt-1">
                    T001,John Doe,30,USA,Electronics,150.50,Credit Card,2024-01-15
                  </div>
                </code>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </AuthGuard>
  );
};

export default NoDataPage;

