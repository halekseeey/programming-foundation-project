'use client';

import { HelpCircle } from 'lucide-react';
import type { RegionsRankingResponse } from '@/lib/api';
import { MetricTooltip } from './MetricTooltip';

interface Props {
	data: RegionsRankingResponse | null;
}

export function RegionsRanking({ data }: Props) {
	if (!data || data.error) {
		return (
			<section className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
				<h2 className="text-lg font-semibold mb-4">Regions Ranking</h2>
				<p className="text-sm text-slate-400">{data?.error || 'No data available'}</p>
			</section>
		);
	}

	return (
		<section className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-6">
			<div className="flex items-center justify-between">
				<div className="flex items-center gap-2">
					<h2 className="text-lg font-semibold">Regions Ranking</h2>
					<MetricTooltip description="Ranking of regions based on renewable energy adoption. Uses renewable energy percentage (%) from the merged dataset (nrg_ind_ren) to identify leading regions, fastest growing regions, and lagging regions.">
						<HelpCircle className="w-3 h-3 text-slate-500 cursor-help" />
					</MetricTooltip>
				</div>
				<div className="flex items-center gap-3">
					{data.metric_used && <span className="text-xs text-slate-400">({data.metric_used})</span>}
					<span className="text-xs text-slate-400">Total: {data.total_regions} regions</span>
				</div>
			</div>

			{/* Leading by Value */}
			{data.leading_by_value && data.leading_by_value.length > 0 && (
				<div>
					<div className="flex items-center gap-2 mb-3">
						<h3 className="text-sm font-semibold text-green-400">Leading by Current Value</h3>
						<MetricTooltip description="Top 10 regions ranked by their current renewable energy percentage (latest year average). These regions have the highest adoption levels, regardless of growth rate.">
							<HelpCircle className="w-3 h-3 text-slate-500 cursor-help" />
						</MetricTooltip>
					</div>
					<div className="space-y-2 max-h-64 overflow-y-auto">
						{data.leading_by_value.map((region, idx) => (
							<div key={idx} className="bg-slate-800/60 rounded-lg p-3">
								<div className="flex items-center justify-between mb-2">
									<div className="flex items-center gap-3">
										<span className="text-xs text-slate-400 w-6">#{idx + 1}</span>
										<span className="text-sm font-semibold">{region.region}</span>
									</div>
									<div className="flex items-center gap-1">
										<span className="text-sm font-bold text-green-400">
											{region.current_value.toFixed(2)}
										</span>
										<MetricTooltip description="Average renewable energy percentage (%) for the latest year in the dataset for this region.">
											<HelpCircle className="w-2.5 h-2.5 text-slate-500 cursor-help" />
										</MetricTooltip>
									</div>
								</div>
								<div className="grid grid-cols-3 gap-2 text-xs">
									<div className="flex items-center gap-1">
										<span className="text-slate-400">Growth rate:</span>
										<MetricTooltip description="Annual change in renewable energy percentage calculated using linear regression. Positive values indicate growth, negative values indicate decline.">
											<HelpCircle className="w-2.5 h-2.5 text-slate-500 cursor-help" />
										</MetricTooltip>
										<span className="ml-1 font-semibold">
											{region.growth_rate >= 0 ? '+' : ''}
											{region.growth_rate.toFixed(3)}
										</span>
									</div>
									<div className="flex items-center gap-1">
										<span className="text-slate-400">Change:</span>
										<MetricTooltip description="Total percentage change from the first year to the last year in the dataset. Calculated as ((last_value - first_value) / first_value) × 100.">
											<HelpCircle className="w-2.5 h-2.5 text-slate-500 cursor-help" />
										</MetricTooltip>
										<span
											className={`ml-1 font-semibold ${
												region.total_change_pct >= 0 ? 'text-green-400' : 'text-red-400'
											}`}
										>
											{region.total_change_pct >= 0 ? '+' : ''}
											{region.total_change_pct.toFixed(2)}%
										</span>
									</div>
									<div className="flex items-center gap-1">
										<span className="text-slate-400">Data points:</span>
										<MetricTooltip description="Number of year observations available for this region in the dataset.">
											<HelpCircle className="w-2.5 h-2.5 text-slate-500 cursor-help" />
										</MetricTooltip>
										<span className="ml-1 font-semibold">{region.data_points}</span>
									</div>
								</div>
							</div>
						))}
					</div>
				</div>
			)}

			{/* Fastest Growing */}
			{data.fastest_growing && data.fastest_growing.length > 0 && (
				<div>
					<div className="flex items-center gap-2 mb-3">
						<h3 className="text-sm font-semibold text-blue-400">Fastest Growing</h3>
						<MetricTooltip description="Top 10 regions with the highest growth rate in renewable energy adoption, regardless of their current level. These regions are increasing their renewable energy percentage the fastest over time.">
							<HelpCircle className="w-3 h-3 text-slate-500 cursor-help" />
						</MetricTooltip>
					</div>
					<div className="space-y-2 max-h-64 overflow-y-auto">
						{data.fastest_growing.map((region, idx) => (
							<div key={idx} className="bg-slate-800/60 rounded-lg p-3">
								<div className="flex items-center justify-between mb-2">
									<div className="flex items-center gap-3">
										<span className="text-xs text-slate-400 w-6">#{idx + 1}</span>
										<span className="text-sm font-semibold">{region.region}</span>
									</div>
									<div className="flex items-center gap-1">
										<span className="text-sm font-bold text-blue-400">
											{region.growth_rate >= 0 ? '+' : ''}
											{region.growth_rate.toFixed(3)}/year
										</span>
										<MetricTooltip description="Annual change in renewable energy percentage calculated using linear regression. This is the slope of the trend line.">
											<HelpCircle className="w-2.5 h-2.5 text-slate-500 cursor-help" />
										</MetricTooltip>
									</div>
								</div>
								<div className="grid grid-cols-3 gap-2 text-xs">
									<div className="flex items-center gap-1">
										<span className="text-slate-400">Current:</span>
										<MetricTooltip description="Average renewable energy percentage (%) for the latest year in the dataset.">
											<HelpCircle className="w-2.5 h-2.5 text-slate-500 cursor-help" />
										</MetricTooltip>
										<span className="ml-1 font-semibold">{region.current_value.toFixed(2)}</span>
									</div>
									<div className="flex items-center gap-1">
										<span className="text-slate-400">Change:</span>
										<MetricTooltip description="Total percentage change from the first year to the last year in the dataset.">
											<HelpCircle className="w-2.5 h-2.5 text-slate-500 cursor-help" />
										</MetricTooltip>
										<span
											className={`ml-1 font-semibold ${
												region.total_change_pct >= 0 ? 'text-green-400' : 'text-red-400'
											}`}
										>
											{region.total_change_pct >= 0 ? '+' : ''}
											{region.total_change_pct.toFixed(2)}%
										</span>
									</div>
									<div className="flex items-center gap-1">
										<span className="text-slate-400">Range:</span>
										<MetricTooltip description="Renewable energy percentage at the first year → last year in the dataset, showing the actual values at the start and end of the period.">
											<HelpCircle className="w-2.5 h-2.5 text-slate-500 cursor-help" />
										</MetricTooltip>
										<span className="ml-1 font-semibold">
											{region.first_value.toFixed(1)} → {region.last_value.toFixed(1)}
										</span>
									</div>
								</div>
							</div>
						))}
					</div>
				</div>
			)}

			{/* Lagging */}
			{data.lagging && data.lagging.length > 0 && (
				<div>
					<div className="flex items-center gap-2 mb-3">
						<h3 className="text-sm font-semibold text-red-400">Lagging Regions</h3>
						<MetricTooltip description="Bottom 10 regions with the lowest current renewable energy percentage. These regions have the lowest adoption levels and may need additional support or policy interventions.">
							<HelpCircle className="w-3 h-3 text-slate-500 cursor-help" />
						</MetricTooltip>
					</div>
					<div className="space-y-2 max-h-64 overflow-y-auto">
						{data.lagging.map((region, idx) => (
							<div key={idx} className="bg-slate-800/60 rounded-lg p-3">
								<div className="flex items-center justify-between mb-2">
									<div className="flex items-center gap-3">
										<span className="text-xs text-slate-400 w-6">#{idx + 1}</span>
										<span className="text-sm font-semibold">{region.region}</span>
									</div>
									<div className="flex items-center gap-1">
										<span className="text-sm font-bold text-red-400">{region.current_value.toFixed(2)}</span>
										<MetricTooltip description="Average renewable energy percentage (%) for the latest year in the dataset for this region.">
											<HelpCircle className="w-2.5 h-2.5 text-slate-500 cursor-help" />
										</MetricTooltip>
									</div>
								</div>
								<div className="grid grid-cols-3 gap-2 text-xs">
									<div className="flex items-center gap-1">
										<span className="text-slate-400">Growth rate:</span>
										<MetricTooltip description="Annual change in renewable energy percentage calculated using linear regression. Positive values indicate growth, negative values indicate decline.">
											<HelpCircle className="w-2.5 h-2.5 text-slate-500 cursor-help" />
										</MetricTooltip>
										<span className="ml-1 font-semibold">
											{region.growth_rate >= 0 ? '+' : ''}
											{region.growth_rate.toFixed(3)}
										</span>
									</div>
									<div className="flex items-center gap-1">
										<span className="text-slate-400">Change:</span>
										<MetricTooltip description="Total percentage change from the first year to the last year in the dataset. Calculated as ((last_value - first_value) / first_value) × 100.">
											<HelpCircle className="w-2.5 h-2.5 text-slate-500 cursor-help" />
										</MetricTooltip>
										<span
											className={`ml-1 font-semibold ${
												region.total_change_pct >= 0 ? 'text-green-400' : 'text-red-400'
											}`}
										>
											{region.total_change_pct >= 0 ? '+' : ''}
											{region.total_change_pct.toFixed(2)}%
										</span>
									</div>
									<div className="flex items-center gap-1">
										<span className="text-slate-400">Data points:</span>
										<MetricTooltip description="Number of year observations available for this region in the dataset.">
											<HelpCircle className="w-2.5 h-2.5 text-slate-500 cursor-help" />
										</MetricTooltip>
										<span className="ml-1 font-semibold">{region.data_points}</span>
									</div>
								</div>
							</div>
						))}
					</div>
				</div>
			)}
		</section>
	);
}
