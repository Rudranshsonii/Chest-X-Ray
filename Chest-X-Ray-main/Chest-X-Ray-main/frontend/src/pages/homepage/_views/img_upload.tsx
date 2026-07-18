import type { PredictResponse, ExplainResponse } from "../../../lib/model";
import { useState, type ChangeEvent } from "react";
import { Upload, Activity, Eye, AlertCircle, CheckCircle, Loader2,} from "lucide-react";
import { predictDiseaseAPI, explainPredictionAPI } from "../../../lib/api";


export default function ImgUpload() {
    const [file, setFile] = useState<File | null>(null);
    const [preview, setPreview] = useState<string | null>(null);
    const [predictions, setPredictions] = useState<PredictResponse | null>(null);
    const [explanation, setExplanation] = useState<ExplainResponse | null>(null);
    const [loading, setLoading] = useState<{ predict: boolean, explain: boolean }>({
        predict: false,
        explain: false
    });
    const [error, setError] = useState<string | null>(null);

    const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
        const selectedFile = event.target.files?.[0];
        if (selectedFile) {
            setFile(selectedFile);
            setPreview(URL.createObjectURL(selectedFile));
            setPredictions(null);
            setExplanation(null);
            setError(null);
        }
    };

    const predictDisease = async (file: File) => {
        setLoading(prev => ({ ...prev, predict: true }));
        setError(null);

        try {
            const data = await predictDiseaseAPI(file);
            setPredictions(data);
            console.log("✅ analyze api response:", data);
        } catch (error) {
            console.error("❌ Prediction error:", error);
            setError(error instanceof Error ? error.message : "Prediction failed");
        } finally {
            setLoading(prev => ({ ...prev, predict: false }));
        }
    };

    const explainPrediction = async (file: File) => {
        setLoading(prev => ({ ...prev, explain: true }));
        setError(null);

        const formData = new FormData();
        formData.append("file", file);
        // const BASE_URL = 'http://0.0.0.0:8007'

        try {
            const data = await explainPredictionAPI(file);
            setExplanation(data);
        } catch (error) {
            console.error("❌ Explanation error:", error);
            setError(error instanceof Error ? error.message : "Explanation failed");
        } finally {
            setLoading(prev => ({ ...prev, explain: false }));
        }
    };

    const handleAnalyze = () => {
        if (file) {
            predictDisease(file);
        }
    };

    const handleExplain = () => {
        if (file) {
            explainPrediction(file);
        }
    };

    const resetUpload = () => {
        setFile(null);
        setPreview(null);
        setPredictions(null);
        setExplanation(null);
        setError(null);
    };

    return (
        <div className="space-y-6">
            {/* Upload Area */}
            <div className="flex items-center justify-center w-full">
                <label
                    htmlFor="dropzone-file"
                    className="flex flex-col items-center justify-center w-full h-64 border-2 border-gray-300 border-dashed rounded-2xl cursor-pointer bg-gray-50 hover:bg-gray-100 transition-colors duration-200"
                >
                    {preview ? (
                        <div className="relative w-full h-full">
                            <img
                                src={preview}
                                alt="Preview"
                                className="h-full w-full object-contain rounded-xl"
                            />
                            <button
                                onClick={(e) => {
                                    e.preventDefault();
                                    resetUpload();
                                }}
                                className="absolute top-2 right-2 p-1 bg-red-500 text-white rounded-full hover:bg-red-600 transition-colors"
                            >
                                ×
                            </button>
                        </div>
                    ) : (
                        <div className="flex flex-col items-center justify-center pt-5 pb-6">
                            <Upload className="w-10 h-10 mb-3 text-gray-400" />
                            <p className="mb-2 text-sm text-gray-500">
                                <span className="font-semibold">Click to upload</span> or drag and drop
                            </p>
                            <p className="text-xs text-gray-400">
                                PNG, JPG (Chest X-ray images)
                            </p>
                        </div>
                    )}
                    <input
                        id="dropzone-file"
                        type="file"
                        accept="image/*"
                        className="hidden"
                        onChange={handleFileChange}
                    />
                </label>
            </div>

            {/* Action Buttons */}
            {file && (
                <div className="flex space-x-4">
                    <button
                        onClick={handleAnalyze}
                        disabled={loading.predict}
                        className="flex-1 flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                        {loading.predict ? (
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        ) : (
                            <Activity className="w-4 h-4 mr-2" />
                        )}
                        {loading.predict ? "Analyzing..." : "Analyze"}
                    </button>

                    <button
                        onClick={handleExplain}
                        disabled={loading.explain}
                        className="flex-1 flex items-center justify-center px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                        {loading.explain ? (
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        ) : (
                            <Eye className="w-4 h-4 mr-2" />
                        )}
                        {loading.explain ? "Generating..." : "Explain"}
                    </button>
                </div>
            )}

            {/* Error Display */}
            {error && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-start space-x-3">
                    <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                    <div>
                        <h3 className="font-medium text-red-900">Error</h3>
                        <p className="text-sm text-red-700">{error}</p>
                    </div>
                </div>
            )}

            {/* Predictions Results */}
            {predictions && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <div className="flex items-center space-x-2 mb-3">
                        <CheckCircle className="w-5 h-5 text-green-600" />
                        <h3 className="font-semibold text-green-900">Analysis Results</h3>
                    </div>

                    <div className="mb-4 p-3 bg-white rounded-lg">
                        <h4 className="font-medium text-gray-900 mb-1">Top Prediction</h4>
                        <div className="flex justify-between items-center">
                            <span className="text-lg font-semibold text-green-700">
                                {predictions.top_prediction.label}
                            </span>
                            <span className="text-sm font-medium bg-green-100 text-green-800 px-2 py-1 rounded">
                                {(predictions.top_prediction.probability * 100).toFixed(1)}%
                            </span>
                        </div>
                    </div>

                    <div>
                        <h4 className="font-medium text-gray-900 mb-2">All Predictions</h4>
                        <div className="space-y-2">
                            {predictions.predictions.map((pred, index) => (

                                <div key={index} className="flex justify-between items-center py-2 px-3 bg-white rounded">
                                    <span className="text-sm text-gray-700">{pred.label}</span>
                                    <div className="flex items-center space-x-2">
                                        <div className="w-20 bg-gray-200 rounded-full h-2">
                                            <div
                                                className="bg-blue-600 h-2 rounded-full"
                                                style={{ width: `${Number(pred.probability) * 100}%` }}
                                            ></div>
                                        </div>
                                        <span className="text-xs text-gray-600 w-12 text-right">
                                            {isFinite(Number(pred.probability)) ? (Number(pred.probability) * 100).toFixed(1) : "0.0"}%
                                        </span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}

            {/* Explanation Results */}
            {explanation && (
                <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                    <div className="flex items-center space-x-2 mb-3">
                        <Eye className="w-5 h-5 text-purple-600" />
                        <h3 className="font-semibold text-purple-900">Visual Explanation</h3>
                    </div>

                    <div className="mb-4">
                        <h4 className="font-medium text-gray-900 mb-2">Grad-CAM Heatmap</h4>
                        <p className="text-sm text-gray-600 mb-3">
                            Red areas show regions the AI focused on for the prediction: <strong>{explanation.explained_prediction.label}</strong>
                        </p>
                        <div className="bg-white p-2 rounded-lg">
                            <img
                                src={`data:image/png;base64,${explanation.heatmap_image}`}
                                alt="Grad-CAM Heatmap"
                                className="w-full h-auto rounded-lg"
                            />
                        </div>
                    </div>

                    <div className="text-xs text-gray-500 space-y-1">
                        <p>Original size: {explanation.image_info.original_size[0]} × {explanation.image_info.original_size[1]}</p>
                        <p>Model input size: {explanation.image_info.model_input_size[0]} × {explanation.image_info.model_input_size[1]}</p>
                    </div>
                </div>
            )}
        </div>
    );
}