// Correlation Analysis component
function renderCorrelationAnalysis(data) {
	if (!data || data.error) {
		document.getElementById('correlation-analysis-container').innerHTML = `
            <section class="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
                <h2 class="text-lg font-semibold mb-4">Correlation Analysis</h2>
                <p class="text-sm text-slate-400">${data?.error || 'No data available'}</p>
            </section>
        `;
		return;
	}

	const strengthColor =
		data.correlation_strength === 'strong'
			? 'text-green-400'
			: data.correlation_strength === 'moderate'
			? 'text-yellow-400'
			: 'text-red-400';

	let chartHtml = '';
	if (data.yearly_averages_plot) {
		const chartId = 'correlation-chart';
		chartHtml = `
            <div>
                <h3 class="text-sm font-semibold mb-3">Yearly Averages Comparison</h3>
                <div class="bg-slate-800/60 rounded-xl p-4">
                    <div id="${chartId}"></div>
                </div>
            </div>
        `;
		setTimeout(() => {
			renderPlotlyChart(chartId, data.yearly_averages_plot);
		}, 300);
	}

	document.getElementById('correlation-analysis-container').innerHTML = `
        <section class="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-6">
            <div class="flex items-center justify-between">
                <h2 class="text-lg font-semibold">Correlation Analysis</h2>
            </div>
            <p class="text-xs text-slate-400">💡 This analysis shows the relationship between renewable energy adoption and ${
				data.indicator_type?.toUpperCase() || 'economic indicators'
			}.</p>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="bg-slate-800/60 rounded-xl p-4">
                    <div class="flex items-center gap-2 mb-1">
                        <p class="text-xs text-slate-400">Overall Correlation</p>
                    </div>
                    <p class="text-2xl font-bold ${data.overall_correlation >= 0 ? 'text-green-400' : 'text-red-400'}">
                        ${data.overall_correlation ? data.overall_correlation.toFixed(3) : 'N/A'}
                    </p>
                </div>

                <div class="bg-slate-800/60 rounded-xl p-4">
                    <div class="flex items-center gap-2 mb-1">
                        <p class="text-xs text-slate-400">Strength</p>
                    </div>
                    <p class="text-2xl font-bold ${strengthColor}">${data.correlation_strength.toUpperCase()}</p>
                </div>

                <div class="bg-slate-800/60 rounded-xl p-4">
                    <div class="flex items-center gap-2 mb-1">
                        <p class="text-xs text-slate-400">Indicator Type</p>
                    </div>
                    <p class="text-2xl font-bold text-sky-400">${data.indicator_type.toUpperCase()}</p>
                </div>
            </div>

            ${chartHtml}

            ${
				data.regional_correlations && data.regional_correlations.length > 0
					? `
                <div>
                    <h3 class="text-sm font-semibold mb-3">Regional Correlations</h3>
                    <div class="h-[300px] overflow-y-auto space-y-2">
                        ${data.regional_correlations
							.slice(0, 20)
							.map(
								(corr, idx) => `
                            <div class="bg-slate-800/60 rounded-lg p-3 flex items-center justify-between w-full">
                                <div class="flex items-center gap-3">
                                    <span class="text-sm font-semibold">${corr.region}</span>
                                    <span class="text-xs text-slate-400">${corr.data_points} pts</span>
                                </div>
                                <p class="text-lg font-bold ${corr.correlation >= 0 ? 'text-green-400' : 'text-red-400'}">
                                    ${corr.correlation >= 0 ? '+' : ''}${corr.correlation.toFixed(3)}
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
        </section>
    `;
}
