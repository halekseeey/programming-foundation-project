// Forecast component for renewable energy forecasting
async function renderForecast(region = null, yearsAhead = 5) {
	const container = document.getElementById('forecast-container');
	if (!container) return;

	try {
		const forecastData = await API.getForecast(region, yearsAhead);

		if (forecastData.error) {
			container.innerHTML = `
				<section class="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
					<h2 class="text-lg font-semibold mb-4">Renewable Energy Forecast</h2>
					<p class="text-sm text-red-400">${forecastData.error}</p>
				</section>
			`;
			return;
		}

		const regionName = forecastData.region || 'Global Average';
		const model = forecastData.model || {};
		const rSquared = (model.r_squared * 100).toFixed(1);

		let chartHtml = '';
		if (forecastData.forecast_plot) {
			const chartId = 'forecast-chart';
			chartHtml = `
				<div class="bg-slate-800/60 rounded-xl p-4">
					<div id="${chartId}"></div>
				</div>
			`;
			setTimeout(() => {
				renderPlotlyChart(chartId, forecastData.forecast_plot);
			}, 100);
		}

		// Forecast summary
		const lastHistorical = forecastData.historical_data[forecastData.historical_data.length - 1];
		const lastForecast = forecastData.forecast_data[forecastData.forecast_data.length - 1];
		const change = lastForecast.value - lastHistorical.value;
		const changePct = ((change / lastHistorical.value) * 100).toFixed(1);

		container.innerHTML = `
			<section class="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-6">
				<div class="flex items-center justify-between">
					<h2 class="text-lg font-semibold">Renewable Energy Forecast</h2>
					<span class="text-xs text-slate-400">${regionName}</span>
				</div>

				<p class="text-xs text-slate-400">📊 Simple linear regression model to estimate future renewable energy shares based on historical trends.</p>

				<!-- Model Quality -->
				<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
					<div class="bg-slate-800/60 rounded-xl p-4">
						<p class="text-xs text-slate-400 mb-1">Model Quality (R²)</p>
						<p class="text-2xl font-bold ${rSquared >= 80 ? 'text-green-400' : rSquared >= 60 ? 'text-yellow-400' : 'text-red-400'}">
							${rSquared}%
						</p>
					</div>
					<div class="bg-slate-800/60 rounded-xl p-4">
						<p class="text-xs text-slate-400 mb-1">Last available</p>
						<p class="text-2xl font-bold text-sky-400">${lastHistorical.value.toFixed(1)}%</p>
						<p class="text-xs text-slate-500 mt-1">${lastHistorical.year}</p>
					</div>
					<div class="bg-slate-800/60 rounded-xl p-4">
						<p class="text-xs text-slate-400 mb-1">Forecast (${lastForecast.year})</p>
						<p class="text-2xl font-bold text-green-400">${lastForecast.value.toFixed(1)}%</p>
						<p class="text-xs ${change >= 0 ? 'text-green-400' : 'text-red-400'} mt-1">
							${change >= 0 ? '+' : ''}${change.toFixed(1)}% (${changePct}%)
						</p>
					</div>
				</div>

				${chartHtml}

				<!-- Forecast Details -->
				<div class="bg-slate-800/60 rounded-xl p-4">
					<h3 class="text-sm font-semibold mb-3">Forecast Details</h3>
					<div class="space-y-2">
						${forecastData.forecast_data.map(item => `
							<div class="flex items-center justify-between text-sm">
								<span class="text-slate-300">${item.year}</span>
								<span class="font-semibold text-green-400">${item.value.toFixed(2)}%</span>
							</div>
						`).join('')}
					</div>
				</div>
			</section>
		`;
	} catch (error) {
		console.error('Failed to load forecast:', error);
		container.innerHTML = `
			<section class="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
				<h2 class="text-lg font-semibold mb-4">Renewable Energy Forecast</h2>
				<p class="text-sm text-red-400">Error loading forecast: ${error.message}</p>
			</section>
		`;
	}
}

