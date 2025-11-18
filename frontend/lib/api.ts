export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5050';

export async function fetchCountries(): Promise<string[]> {
	const res = await fetch(`${API_BASE}/api/countries`);
	const data = await res.json();
	return data.countries ?? [];
}

export interface TimeSeriesPoint {
	year: number;
	value: number;
}

export interface TimeSeriesResponse {
	country: string;
	points: TimeSeriesPoint[];
	summary: {
		first_year?: number;
		last_year?: number;
		first_value?: number;
		last_value?: number;
		abs_change?: number;
		rel_change_pct?: number;
	};
}

export async function fetchTimeSeries(country: string, yearFrom?: number, yearTo?: number): Promise<TimeSeriesResponse> {
	const params = new URLSearchParams({ country });

	if (yearFrom) params.set('year_from', String(yearFrom));
	if (yearTo) params.set('year_to', String(yearTo));

	const res = await fetch(`${API_BASE}/api/timeseries?` + params.toString());
	return res.json();
}

export interface CompareRow {
	country: string;
	year: number;
	value: number;
}

export interface CompareResponse {
	year: number;
	rows: CompareRow[];
}

export async function fetchCompare(countries: string[], year: number): Promise<CompareResponse> {
	const params = new URLSearchParams({
		countries: countries.join(','),
		year: String(year)
	});

	const res = await fetch(`${API_BASE}/api/compare?` + params.toString());
	return res.json();
}

export interface PlotlyFigure {
	data: Array<Record<string, unknown>>;
	layout: Record<string, unknown>;
}

export async function fetchPlotlyFigure(country: string, yearFrom?: number, yearTo?: number): Promise<PlotlyFigure> {
	const params = new URLSearchParams({ country });
	if (yearFrom) params.set('year_from', String(yearFrom));
	if (yearTo) params.set('year_to', String(yearTo));

	const res = await fetch(`${API_BASE}/api/timeseries/plotly?` + params.toString());
	const data = await res.json();
	return data.fig; // dict, который вернул backend
}

// Data Processing APIs

export interface CleanedDataResponse {
	data: Array<Record<string, unknown>>;
	columns: string[];
	rows: number;
}

export async function fetchCleanedData(
	country?: string,
	yearFrom?: number,
	yearTo?: number,
	strategy: string = 'interpolate'
): Promise<CleanedDataResponse> {
	const params = new URLSearchParams();
	if (country) params.set('country', country);
	if (yearFrom) params.set('year_from', String(yearFrom));
	if (yearTo) params.set('year_to', String(yearTo));
	params.set('strategy', strategy);

	const res = await fetch(`${API_BASE}/api/data/clean?` + params.toString());
	return res.json();
}

export interface NUTSResponse {
	country: string;
	nuts_code?: string;
}

export async function fetchNUTSCode(country: string): Promise<NUTSResponse> {
	const params = new URLSearchParams({ country });
	const res = await fetch(`${API_BASE}/api/data/nuts?` + params.toString());
	return res.json();
}

export async function fetchDataWithNUTS(country?: string, yearFrom?: number, yearTo?: number): Promise<CleanedDataResponse> {
	const params = new URLSearchParams();
	if (country) params.set('country', country);
	if (yearFrom) params.set('year_from', String(yearFrom));
	if (yearTo) params.set('year_to', String(yearTo));

	const res = await fetch(`${API_BASE}/api/data/add-nuts?` + params.toString());
	return res.json();
}

export interface SummaryTableResponse {
	data: Array<Record<string, unknown>>;
	columns: string[];
	rows: number;
}

export async function fetchSummaryTable(
	groupBy: string[],
	aggFunctions: string[],
	country?: string,
	yearFrom?: number,
	yearTo?: number
): Promise<SummaryTableResponse> {
	const params = new URLSearchParams({
		group_by: groupBy.join(','),
		agg: aggFunctions.join(',')
	});
	if (country) params.set('country', country);
	if (yearFrom) params.set('year_from', String(yearFrom));
	if (yearTo) params.set('year_to', String(yearTo));

	const res = await fetch(`${API_BASE}/api/data/summary?` + params.toString());
	return res.json();
}

export interface DataQualityReport {
	total_rows: number;
	total_columns: number;
	missing_values: Record<string, number>;
	missing_percentage: Record<string, number>;
	duplicate_rows: number;
	data_types: Record<string, string>;
}

export async function fetchDataQuality(country?: string, yearFrom?: number, yearTo?: number): Promise<DataQualityReport> {
	const params = new URLSearchParams();
	if (country) params.set('country', country);
	if (yearFrom) params.set('year_from', String(yearFrom));
	if (yearTo) params.set('year_to', String(yearTo));

	const res = await fetch(`${API_BASE}/api/data/quality?` + params.toString());
	return res.json();
}

export async function fetchNormalizedData(
	country?: string,
	yearFrom?: number,
	yearTo?: number,
	method: string = 'min_max'
): Promise<CleanedDataResponse> {
	const params = new URLSearchParams({ method });
	if (country) params.set('country', country);
	if (yearFrom) params.set('year_from', String(yearFrom));
	if (yearTo) params.set('year_to', String(yearTo));

	const res = await fetch(`${API_BASE}/api/data/normalize?` + params.toString());
	return res.json();
}

// Dataset Management APIs

export interface Dataset {
	id: string;
	name: string;
	filename: string;
	path: string;
}

export async function fetchDatasets(): Promise<Dataset[]> {
	const res = await fetch(`${API_BASE}/api/datasets`);
	const data = await res.json();
	return data.datasets || [];
}

export async function selectDataset(datasetId: string): Promise<{ dataset_id: string; message: string }> {
	const res = await fetch(`${API_BASE}/api/datasets/select`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ dataset_id: datasetId })
	});
	return res.json();
}

export async function selectDatasets(datasetIds: string[]): Promise<{ dataset_ids: string[]; message: string }> {
	const res = await fetch(`${API_BASE}/api/datasets/select`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ dataset_ids: datasetIds })
	});
	return res.json();
}

export interface DatasetPreview {
	dataset_id: string;
	total_rows: number;
	total_columns: number;
	columns: string[];
	preview: Array<Record<string, unknown>>;
	dtypes: Record<string, string>;
}

export async function fetchDatasetPreview(datasetId: string, rows: number = 10): Promise<DatasetPreview> {
	const res = await fetch(`${API_BASE}/api/datasets/preview?dataset_id=${datasetId}&rows=${rows}`);
	return res.json();
}

export interface CleanDatasetResponse {
	dataset_id: string;
	status: string;
	rows_before: number;
	rows_after: number;
	columns: string[];
	quality_report: DataQualityReport;
	statistics?: {
		missing_values_filled?: number;
		rows_removed?: number;
		invalid_years_removed?: number;
		values_converted?: number;
		nuts_codes_added?: number;
		nuts_codes_failed?: number;
		nuts_codes_failed_values?: string[];
	};
	message: string;
}

export async function cleanDataset(strategy: string = 'interpolate'): Promise<CleanDatasetResponse> {
	const res = await fetch(`${API_BASE}/api/datasets/clean`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ strategy })
	});
	return res.json();
}

// Step 3: Data Analysis APIs
export interface GlobalTrendsResponse {
	overall_growth_rate: number;
	trend_direction: 'increasing' | 'decreasing' | 'stable';
	yearly_averages: Array<{ year: number; average_value: number }>;
	year_over_year_changes: Array<{
		from_year: number;
		to_year: number;
		change_pct: number;
		from_value: number;
		to_value: number;
	}>;
	top_regions: Array<{ region: string; average: number }>;
	period: { from?: number; to?: number };
	metric_used?: string;
	yearly_averages_plot?: PlotlyFigure;
	error?: string;
}

export async function fetchGlobalTrends(yearFrom?: number, yearTo?: number, valueCol?: string): Promise<GlobalTrendsResponse> {
	const params = new URLSearchParams();
	if (yearFrom) params.set('year_from', String(yearFrom));
	if (yearTo) params.set('year_to', String(yearTo));
	if (valueCol) params.set('value_col', valueCol);

	const res = await fetch(`${API_BASE}/api/analysis/global-trends?` + params.toString());
	return res.json();
}

export interface EnergySource {
	source: string;
	average: number;
	total: number;
	min: number;
	max: number;
	data_points: number;
	avg_renewable_pct?: number;
}

export interface EnergySourcesResponse {
	sources: EnergySource[];
	timeseries_by_source: Record<string, Array<{ year: number; value: number }>>;
	source_column: string;
	renewable_pct_available?: boolean;
	timeseries_plot?: PlotlyFigure;
	error?: string;
	available_columns?: string[];
}

export async function fetchEnergySources(yearFrom?: number, yearTo?: number, country?: string): Promise<EnergySourcesResponse> {
	const params = new URLSearchParams();
	if (yearFrom) params.set('year_from', String(yearFrom));
	if (yearTo) params.set('year_to', String(yearTo));
	if (country) params.set('country', country);

	const res = await fetch(`${API_BASE}/api/analysis/energy-sources?` + params.toString());
	return res.json();
}

export interface RegionRanking {
	region: string;
	current_value: number;
	growth_rate: number;
	total_change_pct: number;
	first_value: number;
	last_value: number;
	data_points: number;
}

export interface RegionsRankingResponse {
	leading_by_value: RegionRanking[];
	fastest_growing: RegionRanking[];
	lagging: RegionRanking[];
	total_regions: number;
	metric_used?: string;
	error?: string;
}

export async function fetchRegionsRanking(
	yearFrom?: number,
	yearTo?: number,
	valueCol?: string
): Promise<RegionsRankingResponse> {
	const params = new URLSearchParams();
	if (yearFrom) params.set('year_from', String(yearFrom));
	if (yearTo) params.set('year_to', String(yearTo));
	if (valueCol) params.set('value_col', valueCol);

	const res = await fetch(`${API_BASE}/api/analysis/regions-ranking?` + params.toString());
	return res.json();
}

export interface RegionalCorrelation {
	region: string;
	correlation: number;
	data_points: number;
}

export interface CorrelationResponse {
	indicator_type: string;
	overall_correlation?: number;
	correlation_strength: 'strong' | 'moderate' | 'weak' | 'none';
	regional_correlations: RegionalCorrelation[];
	renewable_trend: { slope: number; intercept: number };
	indicator_trend: { slope: number; intercept: number };
	yearly_averages: Array<{
		year: number;
		renewable_avg: number;
		indicator_avg: number;
	}>;
	yearly_averages_plot?: PlotlyFigure;
	note?: string;
	error?: string;
}

export async function fetchCorrelation(
	indicator: string = 'gdp',
	yearFrom?: number,
	yearTo?: number,
	country?: string,
	valueCol?: string
): Promise<CorrelationResponse> {
	const params = new URLSearchParams({ indicator });
	if (yearFrom) params.set('year_from', String(yearFrom));
	if (yearTo) params.set('year_to', String(yearTo));
	if (country) params.set('country', country);
	if (valueCol) params.set('value_col', valueCol);

	const res = await fetch(`${API_BASE}/api/analysis/correlation?` + params.toString());
	return res.json();
}
