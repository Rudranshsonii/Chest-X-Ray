export interface PredictionResult {
    label: string;
    probability: number;
}

export interface TopPrediction {
    label: string;
    probability: number;
}

export interface PredictResponse {
    filename: string;
    predictions: PredictionResult[];
    top_prediction: TopPrediction;
}

export interface ExplainResponse {
    filename: string;
    heatmap_image: string;
    explained_prediction: {
        label: string;
        probability: number;
        class_index: number;
    };
    image_info: {
        original_size: [number, number];
        model_input_size: [number, number];
    };
}
