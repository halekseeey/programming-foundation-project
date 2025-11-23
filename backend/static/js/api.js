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
	animatedMap: () => fetchJSON(`${API_BASE}/api/analysis/visualizations/animated-map`),
	animatedBar: () => fetchJSON(`${API_BASE}/api/analysis/visualizations/animated-bar`),
	datasetPreview: (dataset = 'merged_dataset', limit = 10) =>
		fetchJSON(`${API_BASE}/api/datasets/${dataset}/preview?limit=${limit}`),
	// New endpoints for filtering
	getRegions: () => fetchJSON(`${API_BASE}/api/filters/regions`),
	getEnergyTypes: () => fetchJSON(`${API_BASE}/api/filters/energy-types`),
	getFilteredAnalysis: (region, energyType, yearFrom, yearTo) => {
		const params = new URLSearchParams();
		if (region) params.append('region', region);
		if (energyType) params.append('energy_type', energyType);
		if (yearFrom) params.append('year_from', yearFrom);
		if (yearTo) params.append('year_to', yearTo);
		return fetchJSON(`${API_BASE}/api/analysis/filtered?${params.toString()}`);
	},
	getFilteredVisualizations: (regions, energyTypes, yearFrom, yearTo) => {
		const params = new URLSearchParams();
		if (regions && regions.length > 0) {
			params.append('regions', regions.join(','));
		}
		if (energyTypes && energyTypes.length > 0) {
			params.append('energy_types', energyTypes.join(','));
		}
		if (yearFrom) params.append('year_from', yearFrom);
		if (yearTo) params.append('year_to', yearTo);
		return fetchJSON(`${API_BASE}/api/analysis/filtered/visualizations?${params.toString()}`);
	},
	getForecast: (region, yearsAhead, yearFrom, yearTo) => {
		const params = new URLSearchParams();
		if (region) params.append('region', region);
		if (yearsAhead) params.append('years_ahead', yearsAhead);
		if (yearFrom) params.append('year_from', yearFrom);
		if (yearTo) params.append('year_to', yearTo);
		return fetchJSON(`${API_BASE}/api/analysis/forecast?${params.toString()}`);
	},
	getMergedDatasetAnalysis: (yearFrom, yearTo) => {
		const params = new URLSearchParams();
		if (yearFrom) params.append('year_from', yearFrom);
		if (yearTo) params.append('year_to', yearTo);
		return fetchJSON(`${API_BASE}/api/analysis/merged-dataset?${params.toString()}`);
	}
};
