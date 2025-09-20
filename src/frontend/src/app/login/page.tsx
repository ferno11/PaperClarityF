import { AuthForm } from "@/components/auth/auth-form";
import { Logo } from "@/components/icons";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function LoginPage() {
  return (
    <div className="relative flex min-h-screen w-full flex-col overflow-hidden bg-[linear-gradient(180deg,_#5E00FF_0%,_#000000_100%)]">
      {/* Background Curves */}
      <div className="absolute top-0 left-0 w-full h-full opacity-10">
        <svg
          className="absolute -top-1/4 -left-1/4 w-full h-full"
          width="1200"
          height="1200"
          viewBox="0 0 1200 1200"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M-200 600C-200 211.929 111.929 -100 500 -100C888.071 -100 1200 211.929 1200 600C1200 988.071 888.071 1300 500 1300C111.929 1300 -200 988.071 -200 600Z"
            stroke="white"
            strokeWidth="2"
          />
        </svg>
        <svg
          className="absolute -bottom-1/4 -right-1/4 w-full h-full"
          width="1200"
          height="1200"
          viewBox="0 0 1200 1200"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M400 600C400 211.929 711.929 -100 1100 -100C1488.07 -100 1800 211.929 1800 600C1800 988.071 1488.07 1300 1100 1300C711.929 1300 400 988.071 400 600Z"
            stroke="white"
            strokeWidth="2"
          />
        </svg>
      </div>

      <div className="w-full h-full flex flex-col lg:flex-row flex-1 z-10">
        {/* Left Side - Branding */}
        <div className="w-full lg:w-1/2 p-8 lg:p-12 flex flex-col justify-center items-center lg:items-start text-center lg:text-left">
           <div className="flex items-center gap-4 mb-6">
            <Logo className="h-14 w-14 text-white" />
            <h1 className="text-5xl font-bold text-white">Paper Clarity</h1>
          </div>
          <p className="text-3xl font-light text-white mb-8">
            AI-powered clarity for your clauses.
          </p>
          <p className="mt-8 max-w-xl text-lg text-gray-300 leading-relaxed">
            Upload your legal documents and let our AI provide easy-to-understand summaries, risk assessments, and answers to your questions. Transform complex contracts into clear, actionable insights.
          </p>
        </div>

        {/* Right Side - Auth */}
        <div className="w-full lg:w-1/2 flex flex-col items-center justify-center p-4">
          <div className="flex items-center gap-4 mb-6 lg:hidden text-white">
            <Logo className="h-12 w-12" />
            <h1 className="text-4xl font-bold">Paper Clarity</h1>
          </div>
          <Card className="w-full max-w-md shadow-2xl">
            <CardHeader className="text-center">
              <CardTitle className="text-xl font-normal text-muted-foreground">
                Sign in to get started
              </CardTitle>
            </CardHeader>
            <CardContent>
              <AuthForm />
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
