// API configuration and helper functions
const API_BASE = window.location.origin;

async function fetchJSON(url) {
	const response = await fetch(url);
	if (!response.ok) {
		throw new Error(`HTTP error! status: ${response.status}`);
	}
	return response.json();
}

const API = {
	globalTrends: () => fetchJSON(`${API_BASE}/api/analysis/global-trends`),
	energySources: () => fetchJSON(`${API_BASE}/api/analysis/energy-sources`),
	regionsRanking: () => fetchJSON(`${API_BASE}/api/analysis/regions-ranking`),
	correlation: (indicator = 'gdp') => fetchJSON(`${API_BASE}/api/analysis/correlation?indicator=${indicator}`),
	heatmap: () => fetchJSON(`${API_BASE}/api/analysis/visualizations/heatmap`),
	map: () => fetchJSON(`${API_BASE}/api/analysis/visualizations/map`),
	animatedMap: () => fetchJSON(`${API_BASE}/api/analysis/visualizations/animated-map`),
	animatedBar: () => fetchJSON(`${API_BASE}/api/analysis/visualizations/animated-bar`),
	datasetPreview: (dataset = 'merged_dataset', limit = 10) =>
		fetchJSON(`${API_BASE}/api/datasets/${dataset}/preview?limit=${limit}`)
};
