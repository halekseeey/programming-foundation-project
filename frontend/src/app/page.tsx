// frontend/app/page.tsx
'use client';

import { useEffect, useState } from 'react';
import {
	cleanDataset,
	fetchGlobalTrends,
	fetchEnergySources,
	fetchRegionsRanking,
	fetchCorrelation,
	type Dataset,
	type CleanDatasetResponse,
	type GlobalTrendsResponse,
	type EnergySourcesResponse,
	type RegionsRankingResponse,
	type CorrelationResponse
} from '@/lib/api';
import { DatasetSelector } from '@/components/DatasetSelector';
import { DatasetPreview } from '@/components/DatasetPreview';
import { GlobalTrends } from '@/components/GlobalTrends';
import { EnergySources } from '@/components/EnergySources';
import { RegionsRanking } from '@/components/RegionsRanking';
import { CorrelationAnalysis } from '@/components/CorrelationAnalysis';

export default function HomePage() {
	// Dataset management
	const [selectedDataset, setSelectedDataset] = useState<Dataset | null>(null);
	const [isDatasetCleaned, setIsDatasetCleaned] = useState(false);
	const [cleaningStatus, setCleaningStatus] = useState<CleanDatasetResponse | null>(null);
	const [cleaning, setCleaning] = useState(false);

	// Step 3: Data Analysis state
	const [globalTrends, setGlobalTrends] = useState<GlobalTrendsResponse | null>(null);
	const [energySources, setEnergySources] = useState<EnergySourcesResponse | null>(null);
	const [regionsRanking, setRegionsRanking] = useState<RegionsRankingResponse | null>(null);
	const [correlation, setCorrelation] = useState<CorrelationResponse | null>(null);

	// Handle dataset selection - automatically clean after selection
	const handleDatasetSelect = async (datasets: Dataset[]) => {
		try {
			if (datasets.length !== 2) {
				console.error('Exactly 2 datasets must be selected');
				return;
			}

			const { selectDatasets } = await import('@/lib/api');
			await selectDatasets(datasets.map((d) => d.id));
			setSelectedDataset(datasets[0]); // Use first for display

			// Automatically start cleaning
			setCleaning(true);
			try {
				const result = await cleanDataset('interpolate');
				setCleaningStatus(result);
				setIsDatasetCleaned(true);
			} catch (error) {
				console.error('Failed to clean dataset:', error);
			} finally {
				setCleaning(false);
			}
		} catch (error) {
			console.error('Failed to select dataset:', error);
		}
	};

	// Load Step 3: Data Analysis when dataset is cleaned
	useEffect(() => {
		if (!isDatasetCleaned) {
			return;
		}

		let cancelled = false;

		// Global trends (no country filter - global analysis)
		fetchGlobalTrends()
			.then((data) => {
				if (!cancelled) {
					setGlobalTrends(data);
				}
			})
			.catch(console.error);

		// Energy sources comparison (global analysis)
		fetchEnergySources()
			.then((data) => {
				if (!cancelled) {
					setEnergySources(data);
				}
			})
			.catch(console.error);

		// Regions ranking (all regions)
		fetchRegionsRanking()
			.then((data) => {
				if (!cancelled) {
					setRegionsRanking(data);
				}
			})
			.catch(console.error);

		// Correlation with indicators (global analysis)
		fetchCorrelation('gdp')
			.then((data) => {
				if (!cancelled) {
					setCorrelation(data);
				}
			})
			.catch(console.error);

		return () => {
			cancelled = true;
		};
	}, [isDatasetCleaned]);

	return (
		<main className="px-6 py-8 max-w-[900px] mx-auto space-y-10">
			{/* Dataset Selection - Show first if no dataset selected */}
			{!selectedDataset ? (
				<DatasetSelector onSelect={handleDatasetSelect} />
			) : (
				<>
					<header className="gap-4 flex justify-between">
						<div className="flex flex-col gap-2">
							<h1 className="text-3xl font-bold tracking-tight">EU Renewable Energy Explorer</h1>
							<p className="text-sm text-slate-400">
								Flask + Python analytics (pandas, numpy, matplotlib, seaborn, plotly) with a Next.js frontend.
							</p>
						</div>

						{selectedDataset && <DatasetPreview datasetId={selectedDataset.id} />}
					</header>

					<section className="bg-slate-900/60 border border-slate-800 rounded-2xl p-4 space-y-2">
						<h3 className="text-sm font-semibold text-white">Dataset Merge Information</h3>
						<p className="text-xs text-slate-300">
							<strong>Smart Merge Strategy:</strong> Datasets are merged using{' '}
							<code className="bg-slate-800 px-1 rounded">geo</code> and{' '}
							<code className="bg-slate-800 px-1 rounded">TIME_PERIOD</code> as keys. The renewable energy
							percentage dataset (<code className="bg-slate-800 px-1 rounded">nrg_ind_ren</code>) is used as the
							main dataset, and corresponding values from the energy balance dataset (
							<code className="bg-slate-800 px-1 rounded">nrg_bal</code>) are added for the same country and year.
							This allows you to analyze correlations between different metrics (percentages vs. absolute values)
							while preserving the structure of the percentage dataset. Empty values (NaN) in merged columns
							indicate that data doesn&apos;t exist in that dataset for that row.
						</p>
					</section>

					{/* Dataset Status - Cleaning happens automatically */}
					{!isDatasetCleaned && (
						<section className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-4">
							<div className="flex items-center justify-between">
								<div>
									<h2 className="text-lg font-semibold">Processing Dataset</h2>
									<p className="text-sm text-slate-400">{selectedDataset.name}</p>
								</div>
								<DatasetPreview datasetId={selectedDataset.id} />
							</div>
							<div className="flex items-center justify-center py-4">
								<div className="text-center space-y-2">
									<div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-sky-500"></div>
									<p className="text-sm text-slate-400">
										{cleaning ? 'Cleaning and Organizing...' : 'Preparing dataset...'}
									</p>
								</div>
							</div>
						</section>
					)}

					{/* Cleaning Status */}
					{cleaningStatus && (
						<section className="bg-green-900/20 border border-green-700 rounded-2xl p-4 space-y-2">
							<p className="text-sm text-green-300 font-semibold">
								✓ {cleaningStatus.message} ({cleaningStatus.rows_before} → {cleaningStatus.rows_after} rows)
							</p>
							{cleaningStatus.statistics && (
								<div className="text-xs text-green-200/80 space-y-1">
									{(cleaningStatus.statistics.missing_values_filled ?? 0) > 0 && (
										<p>• Filled missing values: {cleaningStatus.statistics.missing_values_filled}</p>
									)}
									{(cleaningStatus.statistics.nuts_codes_added ?? 0) > 0 && (
										<p>• Added NUTS codes: {cleaningStatus.statistics.nuts_codes_added}</p>
									)}
									{(cleaningStatus.statistics.values_converted ?? 0) > 0 && (
										<p>• Converted values: {cleaningStatus.statistics.values_converted}</p>
									)}
									{(cleaningStatus.statistics.invalid_years_removed ?? 0) > 0 && (
										<p>
											• Removed rows with invalid years: {cleaningStatus.statistics.invalid_years_removed}
										</p>
									)}
									{(cleaningStatus.statistics.rows_removed ?? 0) > 0 && (
										<p>• Removed rows: {cleaningStatus.statistics.rows_removed}</p>
									)}
									{(cleaningStatus.statistics.nuts_codes_failed ?? 0) > 0 && (
										<div className="text-yellow-300">
											<p>• Failed to determine NUTS codes: {cleaningStatus.statistics.nuts_codes_failed}</p>
											{cleaningStatus.statistics.nuts_codes_failed_values &&
												cleaningStatus.statistics.nuts_codes_failed_values.length > 0 && (
													<div className="mt-1 ml-4 text-xs">
														<span className="text-yellow-200/80">
															Values:{' '}
															{cleaningStatus.statistics.nuts_codes_failed_values.join(', ')}
														</span>
													</div>
												)}
										</div>
									)}
								</div>
							)}
						</section>
					)}

					{/* Analysis Section - Only show after cleaning */}
					{isDatasetCleaned && (
						<>
							{/* Step 3: Data Analysis Section */}
							<section className="space-y-6">
								<h2 className="text-2xl font-bold tracking-tight">Step 3: Data Analysis</h2>
								<p className="text-sm text-slate-400">
									Exploratory analysis using Pandas and NumPy to identify trends, compare energy sources,
									evaluate regional performance, and correlate with economic indicators.
								</p>

								<div className="space-y-6">
									{/* Global Trends */}
									{globalTrends && <GlobalTrends data={globalTrends} />}

									{/* Energy Sources Comparison */}
									{energySources && <EnergySources data={energySources} />}

									{/* Regions Ranking */}
									{regionsRanking && <RegionsRanking data={regionsRanking} />}

									{/* Correlation Analysis (Optional) */}
									{correlation && <CorrelationAnalysis data={correlation} />}
								</div>
							</section>
						</>
					)}
				</>
			)}
		</main>
	);
}
