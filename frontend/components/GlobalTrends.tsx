'use client';

import { HelpCircle } from 'lucide-react';
import type { GlobalTrendsResponse } from '@/lib/api';
import { PlotlyChart } from './PlotlyChart';
import { MetricTooltip } from './MetricTooltip';

interface Props {
	data: GlobalTrendsResponse | null;
}

export function GlobalTrends({ data }: Props) {
	if (!data || data.error) {
		return (
			<section className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
				<h2 className="text-lg font-semibold mb-4">Global Trends Analysis</h2>
				<p className="text-sm text-slate-400">{data?.error || 'No data available'}</p>
			</section>
		);
	}

	const trendColor =
		data.trend_direction === 'increasing'
			? 'text-green-400'
			: data.trend_direction === 'decreasing'
			? 'text-red-400'
			: 'text-yellow-400';

	return (
		<section className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-6">
			<div className="flex items-center justify-between">
				<h2 className="text-lg font-semibold">Global Trends Analysis</h2>
				{data.metric_used && <span className="text-xs text-slate-400">({data.metric_used})</span>}
			</div>

			{/* Overall Growth Rate */}
			<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
				<div className="bg-slate-800/60 rounded-xl p-4">
					<div className="flex items-center gap-2 mb-1">
						<p className="text-xs text-slate-400">Overall Growth Rate</p>
						<MetricTooltip description="Average annual change in renewable energy percentage calculated using linear regression across all years in the dataset. Positive values indicate growth, negative values indicate decline.">
							<HelpCircle className="w-3 h-3 text-slate-500 cursor-help" />
						</MetricTooltip>
					</div>
					<p className={`text-2xl font-bold ${data.overall_growth_rate >= 0 ? 'text-green-400' : 'text-red-400'}`}>
						{data.overall_growth_rate.toFixed(3)} per year
					</p>
				</div>

				<div className="bg-slate-800/60 rounded-xl p-4">
					<div className="flex items-center gap-2 mb-1">
						<p className="text-xs text-slate-400">Trend Direction</p>
						<MetricTooltip description='Overall direction of renewable energy adoption trend. "Increasing" means growth rate > 0.1% per year, "Decreasing" means decline < -0.1% per year, "Stable" means change between -0.1% and 0.1% per year.'>
							<HelpCircle className="w-3 h-3 text-slate-500 cursor-help" />
						</MetricTooltip>
					</div>
					<p className={`text-2xl font-bold ${trendColor}`}>{data.trend_direction.toUpperCase()}</p>
				</div>
			</div>

			{/* Yearly Averages Chart */}
			{data.yearly_averages_plot ? (
				<div>
					<div className="flex items-center gap-2 mb-3">
						<h3 className="text-sm font-semibold">Yearly Averages</h3>
						<MetricTooltip description="Average renewable energy percentage across all regions for each year. Shows the global trend of renewable energy adoption over time.">
							<HelpCircle className="w-3 h-3 text-slate-500 cursor-help" />
						</MetricTooltip>
					</div>
					<div className="bg-slate-800/60 rounded-xl p-4">
						<PlotlyChart data={data.yearly_averages_plot} />
					</div>
				</div>
			) : data.yearly_averages && data.yearly_averages.length > 0 ? (
				<div>
					<h3 className="text-sm font-semibold mb-3">Yearly Averages</h3>
					<p className="text-xs text-slate-400">Chart data available but plot not generated</p>
				</div>
			) : null}

			{/* Year-over-Year Changes */}
			{data.year_over_year_changes && data.year_over_year_changes.length > 0 && (
				<div>
					<div className="flex items-center gap-2 mb-3">
						<h3 className="text-sm font-semibold">Year-over-Year Changes</h3>
						<MetricTooltip description="Percentage change in average renewable energy percentage from one year to the next. Calculated as the difference between consecutive yearly averages divided by the previous year's value.">
							<HelpCircle className="w-3 h-3 text-slate-500 cursor-help" />
						</MetricTooltip>
					</div>
					<div className="space-y-2 max-h-64 overflow-y-auto">
						{data.year_over_year_changes.map((change, idx) => (
							<div key={idx} className="bg-slate-800/60 rounded-lg p-3 flex items-center justify-between">
								<div>
									<p className="text-sm font-semibold">
										{change.from_year} → {change.to_year}
									</p>
									<p className="text-xs text-slate-400">
										{change.from_value.toFixed(2)} → {change.to_value.toFixed(2)}
									</p>
								</div>
								<p className={`text-sm font-bold ${change.change_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
									{change.change_pct >= 0 ? '+' : ''}
									{change.change_pct.toFixed(2)}%
								</p>
							</div>
						))}
					</div>
				</div>
			)}

			{/* Top Regions */}
			{data.top_regions && data.top_regions.length > 0 && (
				<div>
					<div className="flex items-center gap-2 mb-3">
						<h3 className="text-sm font-semibold">Top 10 Regions by Average</h3>
						<MetricTooltip description="Top 10 countries/regions ranked by their average renewable energy percentage across all years in the dataset. Shows which regions have the highest overall renewable energy adoption.">
							<HelpCircle className="w-3 h-3 text-slate-500 cursor-help" />
						</MetricTooltip>
					</div>
					<div className="space-y-2 max-h-64 overflow-y-auto">
						{data.top_regions.map((region, idx) => (
							<div key={idx} className="bg-slate-800/60 rounded-lg p-3 flex items-center justify-between">
								<div className="flex items-center gap-3">
									<span className="text-xs text-slate-400 w-6">#{idx + 1}</span>
									<span className="text-sm font-semibold">{region.region}</span>
								</div>
								<span className="text-sm text-sky-400">{region.average.toFixed(2)}</span>
							</div>
						))}
					</div>
				</div>
			)}
		</section>
	);
}
