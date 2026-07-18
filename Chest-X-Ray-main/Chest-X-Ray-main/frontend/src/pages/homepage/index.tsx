import { Heart} from "lucide-react";
import ImgUpload from "./_views/img_upload";
import { Upload } from "lucide-react";

export default function HomePage() {
    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
            {/* Header */}
            <header className="bg-white shadow-sm border-b">
                <div className="max-w-7xl mx-auto px-4 py-6">
                    <div className="flex items-center space-x-3">
                        <div className="p-2 bg-blue-100 rounded-lg">
                            <Heart className="h-6 w-6 text-blue-600" />
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold text-gray-900">Chest X-Ray Analyzer</h1>
                            <p className="text-sm text-gray-600">AI-powered disease detection and explanation</p>
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="flex justify-center mt-40  px-4">
                <div className="w-full max-w-2xl">
                    {/* Upload Section */}
                    <div className="bg-white rounded-xl shadow-lg p-6">
                        <h2 className="text-xl font-semibold text-gray-900 mb-6 flex items-center">
                            <Upload className="h-5 w-5 mr-2 text-blue-600" />
                            Upload X-Ray Image
                        </h2>
                        <ImgUpload />
                    </div>
                </div>
            </main>

        </div>
    );
}

