// Merged Dataset Analysis component
async function renderMergedDatasetAnalysis() {
	const container = document.getElementById('merged-dataset-analysis-container');
	if (!container) {
		console.error('Merged dataset analysis container not found');
		return;
	}

	try {
		const data = await API.getMergedDatasetAnalysis();

		if (data.error) {
			container.innerHTML = `<p class="text-red-400">Error: ${data.error}</p>`;
			return;
		}

		// Determine correlation strength
		let correlationStrength = '';
		let correlationColor = '';
		if (data.correlation !== null) {
			const absCorr = Math.abs(data.correlation);
			if (absCorr < 0.3) {
				correlationStrength = 'Weak';
				correlationColor = 'text-yellow-400';
			} else if (absCorr < 0.7) {
				correlationStrength = 'Moderate';
				correlationColor = 'text-orange-400';
			} else {
				correlationStrength = 'Strong';
				correlationColor = 'text-green-400';
			}
		}

		// Build HTML
		let html = `
			<section class="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-6">
				<div class="flex items-center justify-between">
					<h2 class="text-lg font-semibold">Merged Dataset Analysis</h2>
				</div>

				<div class="bg-amber-900/20 border border-amber-800/40 rounded-lg p-3 mb-4">
					<p class="font-semibold text-amber-300 mb-1">⚠️ Important Note:</p>
					<p class="text-sm text-slate-300">
						The <code class="bg-slate-700 px-1 rounded">nrg_bal</code> dataset contains categories: 
						Primary production, Exports, Imports, Change in stock, and Recovered and recycled products. 
						However, it does <strong>NOT</strong> contain consumption data. Therefore, this merge combines 
						production data with renewable share data instead of production and consumption data as 
						originally intended.
					</p>
				</div>

				<div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
					<div class="bg-slate-800/60 rounded-xl p-4">
						<p class="text-xs text-slate-400 mb-1">Correlation</p>
						<p class="text-2xl font-bold ${data.correlation >= 0 ? 'text-green-400' : 'text-red-400'}">
							${data.correlation !== null ? data.correlation.toFixed(3) : 'N/A'}
						</p>
						<p class="text-xs text-slate-500 mt-1">Production vs Renewable Share</p>
						${correlationStrength ? `<p class="text-xs ${correlationColor} mt-1 font-semibold">${correlationStrength} correlation</p>` : ''}
					</div>

					<div class="bg-slate-800/60 rounded-xl p-4">
						<p class="text-xs text-slate-400 mb-1">Valid Records</p>
						<p class="text-2xl font-bold text-sky-400">
							${data.summary?.valid_records || 0}
						</p>
						<p class="text-xs text-slate-500 mt-1">of ${data.summary?.total_records || 0} total</p>
					</div>

					<div class="bg-slate-800/60 rounded-xl p-4">
						<p class="text-xs text-slate-400 mb-1">Latest Year</p>
						<p class="text-2xl font-bold text-purple-400">
							${data.latest_year || 'N/A'}
						</p>
					</div>
				</div>

				${
					data.scatter_plot
						? `
					<div class="bg-slate-800/60 rounded-xl p-4">
						<p class="text-xs text-slate-400 mb-3">
							📊 This scatter plot shows the correlation between primary energy production volume and 
							renewable energy share. The size and color of markers represent absolute renewable energy 
							production (production × renewable share). Regions with higher production don't necessarily 
							have higher renewable shares.
						</p>
						<div id="merged-scatter-plot"></div>
					</div>
				`
						: ''
				}

				${
					data.trends_plot
						? `
					<div class="bg-slate-800/60 rounded-xl p-4">
						<p class="text-xs text-slate-400 mb-3">
							📈 This chart shows how average production, renewable share, and absolute renewable energy 
							production have evolved over time. Track whether renewable adoption is accelerating faster 
							than overall production growth.
						</p>
						<div id="merged-trends-plot"></div>
					</div>
				`
						: ''
				}

				${
					data.top_regions_absolute && data.top_regions_absolute.length > 0
						? `
					<div class="bg-slate-800/60 rounded-xl p-4">
						<p class="text-xs text-slate-400 mb-3">
							🏆 Top 10 regions by absolute renewable energy production (${data.latest_year || 'latest year'}):
						</p>
						<div class="space-y-2">
							${data.top_regions_absolute
								.slice(0, 10)
								.map(
									(region, idx) => `
								<div class="flex justify-between items-center p-2 bg-slate-700/40 rounded">
									<span class="text-sm font-semibold">${idx + 1}. ${region.geo}</span>
									<span class="text-xs text-sky-300">${parseFloat(region.absolute_renewable).toLocaleString()} TJ</span>
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
					data.top_regions_share && data.top_regions_share.length > 0
						? `
					<div class="bg-slate-800/60 rounded-xl p-4">
						<p class="text-xs text-slate-400 mb-3">
							🌱 Top 10 regions by renewable energy share (${data.latest_year || 'latest year'}):
						</p>
						<div class="space-y-2">
							${data.top_regions_share
								.slice(0, 10)
								.map(
									(region, idx) => `
								<div class="flex justify-between items-center p-2 bg-slate-700/40 rounded">
									<span class="text-sm font-semibold">${idx + 1}. ${region.geo}</span>
									<span class="text-xs text-green-300">${parseFloat(region.OBS_VALUE_nrg_ind_ren).toFixed(1)}%</span>
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

		container.innerHTML = html;

		// Render plots
		if (data.scatter_plot) {
			setTimeout(() => {
				renderPlotlyChart('merged-scatter-plot', data.scatter_plot);
			}, 100);
		}

		if (data.trends_plot) {
			setTimeout(() => {
				renderPlotlyChart('merged-trends-plot', data.trends_plot);
			}, 200);
		}
	} catch (error) {
		console.error('Error loading merged dataset analysis:', error);
		container.innerHTML = `<p class="text-red-400">Error loading analysis: ${error.message}</p>`;
	}
}
