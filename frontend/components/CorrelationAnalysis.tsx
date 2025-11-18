'use client';

import { HelpCircle } from 'lucide-react';
import type { CorrelationResponse } from '@/lib/api';
import { PlotlyChart } from './PlotlyChart';
import { MetricTooltip } from './MetricTooltip';

interface Props {
	data: CorrelationResponse | null;
}

export function CorrelationAnalysis({ data }: Props) {
	if (!data || data.error) {
		return (
			<section className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
				<h2 className="text-lg font-semibold mb-4">Correlation Analysis</h2>
				<p className="text-sm text-slate-400">{data?.error || 'No data available'}</p>
			</section>
		);
	}

	const correlationColor =
		data.correlation_strength === 'strong'
			? 'text-green-400'
			: data.correlation_strength === 'moderate'
			? 'text-yellow-400'
			: data.correlation_strength === 'weak'
			? 'text-orange-400'
			: 'text-slate-400';

	const correlationBg =
		data.correlation_strength === 'strong'
			? 'bg-green-500/20 border-green-500/50'
			: data.correlation_strength === 'moderate'
			? 'bg-yellow-500/20 border-yellow-500/50'
			: data.correlation_strength === 'weak'
			? 'bg-orange-500/20 border-orange-500/50'
			: 'bg-slate-800/60 border-slate-700';

	return (
		<section className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-6">
			<div className="flex items-center gap-2">
				<h2 className="text-lg font-semibold">Correlation Analysis with {data.indicator_type.toUpperCase()}</h2>
				<MetricTooltip description="Analyzes the relationship between renewable energy adoption and external indicators (GDP, population, etc.). Correlation coefficient ranges from -1 (perfect negative) to +1 (perfect positive), with 0 indicating no correlation.">
					<HelpCircle className="w-3 h-3 text-slate-500 cursor-help" />
				</MetricTooltip>
			</div>

			{/* Overall Correlation */}
			<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
				<div className={`${correlationBg} rounded-xl p-4 border`}>
					<div className="flex items-center gap-2 mb-1">
						<p className="text-xs text-slate-400">Overall Correlation</p>
						<MetricTooltip description="Pearson correlation coefficient calculated across all regions and years. Values close to +1 indicate strong positive correlation (both increase together), values close to -1 indicate strong negative correlation (one increases as the other decreases), values near 0 indicate no correlation.">
							<HelpCircle className="w-2.5 h-2.5 text-slate-500 cursor-help" />
						</MetricTooltip>
					</div>
					<p className={`text-2xl font-bold ${correlationColor}`}>
						{data.overall_correlation ? data.overall_correlation.toFixed(3) : 'N/A'}
					</p>
					<div className="flex items-center gap-2 mt-1">
						<p className="text-xs text-slate-400">Strength:</p>
						<MetricTooltip description="Classification of correlation strength: 'strong' (|r| > 0.7), 'moderate' (0.4 < |r| ≤ 0.7), 'weak' (0 < |r| ≤ 0.4), or 'none' (r ≈ 0 or not calculable).">
							<HelpCircle className="w-2.5 h-2.5 text-slate-500 cursor-help" />
						</MetricTooltip>
						<span className={`text-xs ${correlationColor}`}>{data.correlation_strength}</span>
					</div>
				</div>
				<div className="bg-slate-800/60 rounded-xl p-4">
					<div className="flex items-center gap-2 mb-1">
						<p className="text-xs text-slate-400">Indicator Type</p>
						<MetricTooltip description="External indicator used for correlation analysis (e.g., GDP, population). This represents the variable being compared against renewable energy adoption trends.">
							<HelpCircle className="w-2.5 h-2.5 text-slate-500 cursor-help" />
						</MetricTooltip>
					</div>
					<p className="text-xl font-semibold text-sky-400">{data.indicator_type.toUpperCase()}</p>
				</div>
			</div>

			{/* Correlation Interpretation */}
			{data.overall_correlation && (
				<div className="bg-slate-800/60 rounded-xl p-4">
					<p className="text-sm text-slate-300">
						{Math.abs(data.overall_correlation) > 0.7 ? (
							<span>
								<strong className="text-green-400">Strong correlation</strong> - Renewable energy trends show a{' '}
								{data.overall_correlation > 0 ? 'positive' : 'negative'} relationship with{' '}
								{data.indicator_type.toUpperCase()}.
							</span>
						) : Math.abs(data.overall_correlation) > 0.4 ? (
							<span>
								<strong className="text-yellow-400">Moderate correlation</strong> - There is a
								{data.overall_correlation > 0 ? ' positive' : ' negative'} relationship between renewable energy
								and {data.indicator_type.toUpperCase()}, but it&apos;s not very strong.
							</span>
						) : (
							<span>
								<strong className="text-orange-400">Weak correlation</strong> - Little to no clear relationship
								between renewable energy and {data.indicator_type.toUpperCase()}.
							</span>
						)}
					</p>
				</div>
			)}

			{/* Yearly Averages Comparison */}
			{data.yearly_averages_plot ? (
				<div>
					<div className="flex items-center gap-2 mb-3">
						<h3 className="text-sm font-semibold">Yearly Averages Comparison</h3>
						<MetricTooltip description="Comparison of average renewable energy percentage and indicator values over time. Shows how both variables evolve together, helping visualize the correlation relationship across years.">
							<HelpCircle className="w-3 h-3 text-slate-500 cursor-help" />
						</MetricTooltip>
					</div>
					<div className="bg-slate-800/60 rounded-xl p-4">
						<PlotlyChart data={data.yearly_averages_plot} />
					</div>
				</div>
			) : data.yearly_averages && data.yearly_averages.length > 0 ? (
				<div>
					<div className="flex items-center gap-2 mb-3">
						<h3 className="text-sm font-semibold">Yearly Averages Comparison</h3>
						<MetricTooltip description="Comparison of average renewable energy percentage and indicator values over time. Shows how both variables evolve together, helping visualize the correlation relationship across years.">
							<HelpCircle className="w-3 h-3 text-slate-500 cursor-help" />
						</MetricTooltip>
					</div>
					<p className="text-xs text-slate-400">Chart data available but plot not generated</p>
				</div>
			) : null}

			{/* Regional Correlations */}
			{data.regional_correlations && data.regional_correlations.length > 0 && (
				<div>
					<div className="flex items-center gap-2 mb-3">
						<h3 className="text-sm font-semibold">Regional Correlations</h3>
						<MetricTooltip description="Correlation coefficient calculated separately for each region. Shows which regions have stronger or weaker relationships between renewable energy and the indicator. Top 20 regions are displayed, sorted by correlation strength.">
							<HelpCircle className="w-3 h-3 text-slate-500 cursor-help" />
						</MetricTooltip>
					</div>
					<div className="space-y-2 max-h-96 overflow-y-auto">
						{data.regional_correlations.map((region, idx) => {
							const regColor =
								Math.abs(region.correlation) > 0.7
									? 'text-green-400'
									: Math.abs(region.correlation) > 0.4
									? 'text-yellow-400'
									: 'text-orange-400';
							return (
								<div key={idx} className="bg-slate-800/60 rounded-lg p-3 flex items-center justify-between">
									<div className="flex items-center gap-3">
										<span className="text-xs text-slate-400 w-6">#{idx + 1}</span>
										<span className="text-sm font-semibold">{region.region}</span>
									</div>
									<div className="flex items-center gap-4">
										<div className="flex items-center gap-1">
											<span className={`text-sm font-bold ${regColor}`}>
												{region.correlation >= 0 ? '+' : ''}
												{region.correlation.toFixed(3)}
											</span>
											<MetricTooltip description="Pearson correlation coefficient for this specific region. Calculated using all available year observations for this region only.">
												<HelpCircle className="w-2.5 h-2.5 text-slate-500 cursor-help" />
											</MetricTooltip>
										</div>
										<div className="flex items-center gap-1">
											<span className="text-xs text-slate-400">({region.data_points} points)</span>
											<MetricTooltip description="Number of year observations used to calculate the correlation for this region.">
												<HelpCircle className="w-2.5 h-2.5 text-slate-500 cursor-help" />
											</MetricTooltip>
										</div>
									</div>
								</div>
							);
						})}
					</div>
				</div>
			)}

			{/* Trend Lines */}
			{data.renewable_trend && data.indicator_trend && (
				<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
					<div className="bg-slate-800/60 rounded-xl p-4">
						<div className="flex items-center gap-2 mb-1">
							<p className="text-xs text-slate-400">Renewable Energy Trend</p>
							<MetricTooltip description="Linear regression parameters for renewable energy percentage over time. Slope indicates the annual rate of change, intercept is the value at year 0. Formula: renewable_energy = slope × year + intercept.">
								<HelpCircle className="w-2.5 h-2.5 text-slate-500 cursor-help" />
							</MetricTooltip>
						</div>
						<div className="flex items-center gap-2">
							<p className="text-sm font-semibold">
								Slope: <span className="text-sky-400">{data.renewable_trend.slope.toFixed(4)}</span>
							</p>
							<MetricTooltip description="Annual change rate in renewable energy percentage. Positive values indicate growth, negative values indicate decline.">
								<HelpCircle className="w-2.5 h-2.5 text-slate-500 cursor-help" />
							</MetricTooltip>
						</div>
						<div className="flex items-center gap-2 mt-1">
							<p className="text-xs text-slate-400">Intercept: {data.renewable_trend.intercept.toFixed(2)}</p>
							<MetricTooltip description="Renewable energy percentage value at the theoretical year 0 (baseline value of the trend line).">
								<HelpCircle className="w-2.5 h-2.5 text-slate-500 cursor-help" />
							</MetricTooltip>
						</div>
					</div>
					<div className="bg-slate-800/60 rounded-xl p-4">
						<div className="flex items-center gap-2 mb-1">
							<p className="text-xs text-slate-400">{data.indicator_type.toUpperCase()} Trend</p>
							<MetricTooltip description="Linear regression parameters for the indicator (GDP, population, etc.) over time. Slope indicates the annual rate of change, intercept is the value at year 0. Formula: indicator = slope × year + intercept.">
								<HelpCircle className="w-2.5 h-2.5 text-slate-500 cursor-help" />
							</MetricTooltip>
						</div>
						<div className="flex items-center gap-2">
							<p className="text-sm font-semibold">
								Slope: <span className="text-green-400">{data.indicator_trend.slope.toFixed(4)}</span>
							</p>
							<MetricTooltip description="Annual change rate in the indicator value. Positive values indicate growth, negative values indicate decline.">
								<HelpCircle className="w-2.5 h-2.5 text-slate-500 cursor-help" />
							</MetricTooltip>
						</div>
						<div className="flex items-center gap-2 mt-1">
							<p className="text-xs text-slate-400">Intercept: {data.indicator_trend.intercept.toFixed(2)}</p>
							<MetricTooltip description="Indicator value at the theoretical year 0 (baseline value of the trend line).">
								<HelpCircle className="w-2.5 h-2.5 text-slate-500 cursor-help" />
							</MetricTooltip>
						</div>
					</div>
				</div>
			)}
		</section>
	);
}
