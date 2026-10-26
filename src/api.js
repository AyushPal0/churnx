const API_URL = (import.meta.env?.VITE_API_URL || '/api').replace(/\/$/, '');

export async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    signal: options.signal || AbortSignal.timeout(15000),
    headers: { 'Content-Type': 'application/json', ...options.headers },
  });
  if (!response.ok) {
    if (response.status === 422) throw new Error('Please check the customer information. The service rejected one or more fields.');
    throw new Error('The prediction service is unavailable. Check that the backend is running and try again.');
  }
  return response.json();
}

export function normalizePrediction(payload) {
  const probability = payload.churn_probability;
  if (typeof probability !== 'number' || !Number.isFinite(probability) || probability < 0 || probability > 1 || ![0, 1].includes(payload.prediction) || !['LOW', 'MEDIUM', 'HIGH'].includes(payload.risk_level)) {
    throw new Error('The service returned an invalid prediction. Please try again.');
  }
  return {
    probability: Math.round(probability * 10000) / 100,
    risk: payload.risk_level[0] + payload.risk_level.slice(1).toLowerCase(),
    classification: payload.prediction === 1 ? 'Likely to churn' : 'Likely to stay',
    reasons: Array.isArray(payload.top_factors) ? payload.top_factors : [],
    modelVersion: payload.model_version, explanationMethod: payload.explanation_method,
  };
}
