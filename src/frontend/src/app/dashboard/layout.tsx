import AppHeader from "@/components/layout/app-header";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="relative flex min-h-screen w-full flex-col bg-[linear-gradient(180deg,_#5E00FF_0%,_#000000_100%)]">
      {/* Background Curves */}
      <div className="absolute top-0 left-0 w-full h-full opacity-10 -z-10">
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
      
      <AppHeader />
      <main className="flex-1 p-4 sm:px-6 sm:py-4 md:gap-8">
        {children}
      </main>
    </div>
  );
}
