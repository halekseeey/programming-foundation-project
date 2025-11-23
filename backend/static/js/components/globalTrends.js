// Global Trends component
function renderGlobalTrends(data) {
	if (!data || data.error) {
		document.getElementById('global-trends-container').innerHTML = `
            <section class="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
                <h2 class="text-lg font-semibold mb-4">Global Trends Analysis</h2>
                <p class="text-sm text-slate-400">${data?.error || 'No data available'}</p>
            </section>
        `;
		return;
	}

	const trendColor =
		data.trend_direction === 'increasing'
			? 'text-green-400'
			: data.trend_direction === 'decreasing'
			? 'text-red-400'
			: 'text-yellow-400';

	let chartHtml = '';
	if (data.yearly_averages_plot) {
		const chartId = 'global-trends-chart';
		chartHtml = `
            <div>
                <div class="flex items-center gap-2 mb-3">
                    <h3 class="text-sm font-semibold">Yearly Averages</h3>
                </div>
                <div class="bg-slate-800/60 rounded-xl p-4">
                    <div id="${chartId}"></div>
                </div>
            </div>
        `;
		setTimeout(() => {
			renderPlotlyChart(chartId, data.yearly_averages_plot);
		}, 100);
	}

	document.getElementById('global-trends-container').innerHTML = `
        <section class="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-6">
            <div class="flex items-center justify-between">
                <h2 class="text-lg font-semibold">Global Trends Analysis</h2>
                ${data.metric_used ? `<span class="text-xs text-slate-400">(${data.metric_used})</span>` : ''}
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="bg-slate-800/60 rounded-xl p-4">
                    <div class="flex items-center gap-2 mb-1">
                        <p class="text-xs text-slate-400">Overall Growth Rate</p>
                    </div>
                    <p class="text-2xl font-bold ${data.overall_growth_rate >= 0 ? 'text-green-400' : 'text-red-400'}">
                        ${data.overall_growth_rate.toFixed(3)} per year
                    </p>
                </div>

                <div class="bg-slate-800/60 rounded-xl p-4">
                    <div class="flex items-center gap-2 mb-1">
                        <p class="text-xs text-slate-400">Trend Direction</p>
                    </div>
                    <p class="text-2xl font-bold ${trendColor}">${data.trend_direction.toUpperCase()}</p>
                </div>
            </div>

            <div class="bg-slate-800/60 rounded-xl p-4">
                <p class="text-xs text-slate-400 mb-2">📊 This chart shows the average renewable energy share (%) across all regions over time.</p>
                ${chartHtml}
            </div>

            ${
				data.year_over_year_changes && data.year_over_year_changes.length > 0
					? `
                <div>
                    <h3 class="text-sm font-semibold mb-3">Year-over-Year Changes</h3>
                    <div class="h-[300px] overflow-y-auto space-y-2">
                        ${data.year_over_year_changes
							.map(
								(change, idx) => `
                            <div class="bg-slate-800/60 rounded-lg p-3 flex items-center justify-between w-full">
                                <div>
                                    <p class="text-sm font-semibold">${change.from_year} → ${change.to_year}</p>
                                    <p class="text-xs text-slate-400">
                                        ${change.from_value.toFixed(2)} → ${change.to_value.toFixed(2)}
                                    </p>
                                </div>
                                <p class="text-sm font-bold ${change.change_pct >= 0 ? 'text-green-400' : 'text-red-400'}">
                                    ${change.change_pct >= 0 ? '+' : ''}${change.change_pct.toFixed(2)}%
                                </p>
                            </div>
                        `
							)
							.join('')}
                    </div>
                </div>
            `
					: ''
			}

            ${
				data.top_regions && data.top_regions.length > 0
					? `
                <div>
                    <h3 class="text-sm font-semibold mb-3">Top 10 Regions by Average</h3>
                    <div class="h-[300px] overflow-y-auto space-y-2">
                        ${data.top_regions
							.map(
								(region, idx) => `
                            <div class="bg-slate-800/60 rounded-lg p-3 flex items-center justify-between w-full">
                                <div class="flex items-center gap-3">
                                    <span class="text-xs text-slate-400 w-6">#${idx + 1}</span>
                                    <span class="text-sm font-semibold">${region.region}</span>
                                </div>
                                <span class="text-sm text-sky-400">${region.average.toFixed(2)}</span>
                            </div>
                        `
							)
							.join('')}
                    </div>
                </div>
            `
					: ''
			}
        </section>
    `;
}
