// api/predict.ts
const BASE_URL = 'http://0.0.0.0:8007'

export const predictDiseaseAPI = async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${BASE_URL}/api/predict`, {
        method: "POST",
        body: formData,
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || "Prediction failed");
    }

    const result = await response.json();

    if (!result.success) {
        throw new Error(result.message || "Prediction failed");
    }
    console.log("predict response:",result)

    // Normalize data
    return {
        ...result.data,
        predictions: result.data.predictions.map((pred: any) => ({
            label: pred.label,
            probability: pred.prob,
        })),
        top_prediction: {
            label: result.data.top_prediction.label,
            probability: result.data.top_prediction.probability,
        },
    };
};

export const explainPredictionAPI = async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${BASE_URL}/api/explain`, {
        method: "POST",
        body: formData,
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || "Explanation failed");
    }

    const result = await response.json();
    if (!result.success) {
        throw new Error(result.message || "Explanation failed");
    }
    console.log("explain response:", result)

    return result.data; // 🔥 only return the useful data
  };