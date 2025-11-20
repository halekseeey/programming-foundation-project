// Energy Sources component
function renderEnergySources(data) {
	if (!data || data.error) {
		document.getElementById('energy-sources-container').innerHTML = `
            <section class="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
                <h2 class="text-lg font-semibold mb-4">Energy Sources Comparison</h2>
                <p class="text-sm text-slate-400">${data?.error || 'No data available'}</p>
            </section>
        `;
		return;
	}

	let barChartHtml = '';
	if (data.bar_chart_plot && data.bar_chart_plot.data && data.bar_chart_plot.data.length > 0) {
		const chartId = 'energy-sources-bar-chart';
		barChartHtml = `
            <div>
                <h3 class="text-sm font-semibold mb-3">Energy Sources Comparison (Bar Chart)</h3>
                <div class="bg-slate-800/60 rounded-xl p-4">
                    <div id="${chartId}" style="min-height: 400px;"></div>
                </div>
            </div>
        `;
		setTimeout(() => {
			renderPlotlyChart(chartId, data.bar_chart_plot);
		}, 200);
	}

	let timeSeriesChartHtml = '';
	if (data.timeseries_plot) {
		const chartId = 'energy-sources-timeseries';
		timeSeriesChartHtml = `
            <div>
                <h3 class="text-sm font-semibold mb-3">Time Series by Source</h3>
                <div class="bg-slate-800/60 rounded-xl p-4">
                    <div id="${chartId}"></div>
                </div>
            </div>
        `;
		setTimeout(() => {
			renderPlotlyChart(chartId, data.timeseries_plot);
		}, 300);
	}

	document.getElementById('energy-sources-container').innerHTML = `
        <section class="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-6">
            <div class="flex items-center justify-between">
                <h2 class="text-lg font-semibold">Energy Sources Comparison</h2>
                ${data.source_column ? `<span class="text-xs text-slate-400">Source: ${data.source_column}</span>` : ''}
            </div>
            <p class="text-xs text-blue-300/80">
                ℹ️ All data from energy balance dataset (nrg_bal) with detailed source breakdown by region and year.
            </p>

            ${barChartHtml}

            ${
				data.sources && data.sources.length > 0
					? `
                <div>
                    <h3 class="text-sm font-semibold mb-3">Sources Statistics</h3>
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        ${data.sources
							.map(
								(source, idx) => `
                            <div class="bg-slate-800/60 rounded-xl p-4 space-y-2">
                                <h3 class="text-sm font-semibold text-sky-400">${source.source}</h3>
                                <div class="space-y-1 text-xs">
                                    <div class="flex justify-between items-center">
                                        <span class="text-slate-400">Average:</span>
                                        <span class="font-semibold">${source.average.toFixed(2)}</span>
                                    </div>
                                    <div class="flex justify-between items-center">
                                        <span class="text-slate-400">Total:</span>
                                        <span class="font-semibold">${source.total.toFixed(2)}</span>
                                    </div>
                                    <div class="flex justify-between items-center">
                                        <span class="text-slate-400">Min:</span>
                                        <span class="font-semibold">${source.min.toFixed(2)}</span>
                                    </div>
                                    <div class="flex justify-between items-center">
                                        <span class="text-slate-400">Max:</span>
                                        <span class="font-semibold">${source.max.toFixed(2)}</span>
                                    </div>
                                    <div class="flex justify-between items-center">
                                        <span class="text-slate-400">Data points:</span>
                                        <span class="font-semibold">${source.data_points}</span>
                                    </div>
                                    ${
										source.share_of_total != null
											? `
                                        <div class="flex justify-between items-center pt-1 border-t border-slate-700">
                                            <span class="text-green-300">Share of Total:</span>
                                            <span class="font-semibold text-green-400">${source.share_of_total.toFixed(2)}%</span>
                                        </div>
                                    `
											: ''
									}
                                    ${
										source.growth_rate != null
											? `
                                        <div class="flex justify-between items-center">
                                            <span class="text-yellow-300">Growth Rate:</span>
                                            <span class="font-semibold ${
												source.growth_rate >= 0 ? 'text-yellow-400' : 'text-red-400'
											}">
                                                ${source.growth_rate >= 0 ? '+' : ''}${source.growth_rate.toFixed(2)}% per year
                                            </span>
                                        </div>
                                    `
											: ''
									}
                                </div>
                            </div>
                        `
							)
							.join('')}
                    </div>
                </div>
            `
					: ''
			}

            ${timeSeriesChartHtml}
        </section>
    `;
}

