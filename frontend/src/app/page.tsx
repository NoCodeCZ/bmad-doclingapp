export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm lg:flex">
        <h1 className="text-4xl font-bold text-center">
          Workshop Document Processor
        </h1>
      </div>
      <div className="text-center">
        <p className="text-xl mb-4">
          Convert office documents to AI-optimized markdown format
        </p>
        <p className="text-gray-600">
          Upload your PDF, DOCX, PPTX, or XLSX files to get started
        </p>
      </div>
    </main>
  );
}