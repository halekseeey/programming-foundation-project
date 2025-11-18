'use client';

import { HelpCircle } from 'lucide-react';
import type { EnergySourcesResponse } from '@/lib/api';
import { PlotlyChart } from './PlotlyChart';
import { MetricTooltip } from './MetricTooltip';

interface Props {
	data: EnergySourcesResponse | null;
}

export function EnergySources({ data }: Props) {
	if (!data || data.error) {
		return (
			<section className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
				<h2 className="text-lg font-semibold mb-4">Energy Sources Comparison</h2>
				<p className="text-sm text-slate-400">
					{data?.error || 'No data available'}
					{data?.available_columns && (
						<span className="block mt-2 text-xs">Available columns: {data.available_columns.join(', ')}</span>
					)}
				</p>
			</section>
		);
	}

	return (
		<section className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-6">
			<div className="flex items-center justify-between">
				<h2 className="text-lg font-semibold">Energy Sources Comparison</h2>
				{data.source_column && <span className="text-xs text-slate-400">Source: {data.source_column}</span>}
			</div>
			{data.renewable_pct_available && (
				<p className="text-xs text-blue-300/80">ℹ️ Renewable energy percentage context available from merged dataset</p>
			)}

			{/* Sources Statistics */}
			{data.sources && data.sources.length > 0 && (
				<div>
					<div className="flex items-center gap-2 mb-3">
						<h3 className="text-sm font-semibold">Sources Statistics</h3>
						<MetricTooltip description="Statistical summary for each energy source type (solar, wind, hydro, biomass, etc.) from the energy balance dataset. Shows average, total, min, max values and number of data points. If available, also displays average renewable energy percentage from the merged dataset.">
							<HelpCircle className="w-3 h-3 text-slate-500 cursor-help" />
						</MetricTooltip>
					</div>
					<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
						{data.sources.map((source, idx) => (
							<div key={idx} className="bg-slate-800/60 rounded-xl p-4 space-y-2">
								<h3 className="text-sm font-semibold text-sky-400">{source.source}</h3>
								<div className="space-y-1 text-xs">
									<div className="flex justify-between items-center">
										<div className="flex items-center gap-1">
											<span className="text-slate-400">Average:</span>
											<MetricTooltip description="Mean energy value (in GWh) for this source across all regions and years in the dataset.">
												<HelpCircle className="w-2.5 h-2.5 text-slate-500 cursor-help" />
											</MetricTooltip>
										</div>
										<span className="font-semibold">{source.average.toFixed(2)}</span>
									</div>
									<div className="flex justify-between items-center">
										<div className="flex items-center gap-1">
											<span className="text-slate-400">Total:</span>
											<MetricTooltip description="Sum of all energy values (in GWh) for this source across all data points.">
												<HelpCircle className="w-2.5 h-2.5 text-slate-500 cursor-help" />
											</MetricTooltip>
										</div>
										<span className="font-semibold">{source.total.toFixed(2)}</span>
									</div>
									<div className="flex justify-between items-center">
										<div className="flex items-center gap-1">
											<span className="text-slate-400">Min:</span>
											<MetricTooltip description="Minimum energy value (in GWh) observed for this source in the dataset.">
												<HelpCircle className="w-2.5 h-2.5 text-slate-500 cursor-help" />
											</MetricTooltip>
										</div>
										<span className="font-semibold">{source.min.toFixed(2)}</span>
									</div>
									<div className="flex justify-between items-center">
										<div className="flex items-center gap-1">
											<span className="text-slate-400">Max:</span>
											<MetricTooltip description="Maximum energy value (in GWh) observed for this source in the dataset.">
												<HelpCircle className="w-2.5 h-2.5 text-slate-500 cursor-help" />
											</MetricTooltip>
										</div>
										<span className="font-semibold">{source.max.toFixed(2)}</span>
									</div>
									<div className="flex justify-between items-center">
										<div className="flex items-center gap-1">
											<span className="text-slate-400">Data points:</span>
											<MetricTooltip description="Total number of observations (region-year combinations) available for this energy source.">
												<HelpCircle className="w-2.5 h-2.5 text-slate-500 cursor-help" />
											</MetricTooltip>
										</div>
										<span className="font-semibold">{source.data_points}</span>
									</div>
									{source.avg_renewable_pct != null && (
										<div className="flex justify-between items-center pt-1 border-t border-slate-700">
											<div className="flex items-center gap-1">
												<span className="text-blue-300">Avg Renewable %:</span>
												<MetricTooltip description="Average renewable energy percentage for regions and years where this source is present. This value comes from the merged dataset (nrg_ind_ren) and provides context about overall renewable energy adoption in areas using this source.">
													<HelpCircle className="w-2.5 h-2.5 text-blue-400 cursor-help" />
												</MetricTooltip>
											</div>
											<span className="font-semibold text-blue-400">
												{source.avg_renewable_pct.toFixed(2)}%
											</span>
										</div>
									)}
								</div>
							</div>
						))}
					</div>
				</div>
			)}

			{/* Time Series by Source */}
			{data.timeseries_plot ? (
				<div>
					<div className="flex items-center gap-2 mb-3">
						<h3 className="text-sm font-semibold">Time Series by Source</h3>
						<MetricTooltip description="Evolution of energy production/consumption (in GWh) over time for each energy source type. Each line represents a different source (solar, wind, hydro, etc.), showing how their contribution to the energy mix has changed across years.">
							<HelpCircle className="w-3 h-3 text-slate-500 cursor-help" />
						</MetricTooltip>
					</div>
					<div className="bg-slate-800/60 rounded-xl p-4">
						<PlotlyChart data={data.timeseries_plot} />
					</div>
				</div>
			) : data.timeseries_by_source && Object.keys(data.timeseries_by_source).length > 0 ? (
				<div>
					<div className="flex items-center gap-2 mb-3">
						<h3 className="text-sm font-semibold">Time Series by Source</h3>
						<MetricTooltip description="Evolution of energy production/consumption (in GWh) over time for each energy source type. Each line represents a different source (solar, wind, hydro, etc.), showing how their contribution to the energy mix has changed across years.">
							<HelpCircle className="w-3 h-3 text-slate-500 cursor-help" />
						</MetricTooltip>
					</div>
					<p className="text-xs text-slate-400">Chart data available but plot not generated</p>
				</div>
			) : null}
		</section>
	);
}
