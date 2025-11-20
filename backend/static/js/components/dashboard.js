// Dashboard component with main insights
async function renderDashboard() {
	const container = document.getElementById('dashboard-container');
	if (!container) return;

	try {
		const data = await API.getDashboard();

		if (data.error) {
			container.innerHTML = `
				<section class="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
					<h2 class="text-lg font-semibold mb-4">Dashboard</h2>
					<p class="text-sm text-slate-400">${data.error}</p>
				</section>
			`;
			return;
		}

		const growthRate = data.global_trends?.growth_rate || 0;
		const trendDirection = data.global_trends?.trend_direction || 'stable';
		const latestAverage = data.global_trends?.latest_average || 0;

		const trendColor =
			trendDirection === 'increasing'
				? 'text-green-400'
				: trendDirection === 'decreasing'
				? 'text-red-400'
				: 'text-yellow-400';
		const trendIcon = trendDirection === 'increasing' ? '↑' : trendDirection === 'decreasing' ? '↓' : '→';

		let html = `
			<section class="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-6">
				<h2 class="text-lg font-semibold">Dashboard - Main Insights</h2>
				
				<!-- Key Metrics -->
				<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
					<div class="bg-slate-800/60 rounded-xl p-4 border border-slate-700">
						<p class="text-xs text-slate-400 mb-1">Global Renewable Energy Share</p>
						<p class="text-2xl font-bold text-sky-400">${latestAverage.toFixed(2)}%</p>
						<p class="text-xs text-slate-500 mt-1">Latest year average</p>
					</div>
					<div class="bg-slate-800/60 rounded-xl p-4 border border-slate-700">
						<p class="text-xs text-slate-400 mb-1">Overall Growth Rate</p>
						<p class="text-2xl font-bold ${trendColor}">${growthRate > 0 ? '+' : ''}${growthRate.toFixed(2)}%</p>
						<p class="text-xs text-slate-500 mt-1">Annual growth ${trendIcon}</p>
					</div>
					<div class="bg-slate-800/60 rounded-xl p-4 border border-slate-700">
						<p class="text-xs text-slate-400 mb-1">Trend Direction</p>
						<p class="text-2xl font-bold ${trendColor}">${trendDirection}</p>
						<p class="text-xs text-slate-500 mt-1">Overall trend</p>
					</div>
				</div>
				
				<!-- Top Regions -->
				<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
					<div class="bg-slate-800/60 rounded-xl p-4 border border-slate-700">
						<h3 class="text-sm font-semibold mb-3 text-green-400">Top 5 Leading Regions</h3>
						<div class="space-y-2">
							${
								(data.top_regions || [])
									.map(
										(region, idx) => `
								<div class="flex items-center justify-between text-xs">
									<span class="text-slate-300">${idx + 1}. ${region.region || 'N/A'}</span>
									<span class="font-semibold text-green-400">${(region.current_value || 0).toFixed(2)}%</span>
								</div>
							`
									)
									.join('') || '<p class="text-xs text-slate-500">No data available</p>'
							}
						</div>
					</div>
					
					<div class="bg-slate-800/60 rounded-xl p-4 border border-slate-700">
						<h3 class="text-sm font-semibold mb-3 text-blue-400">Top 5 Fastest Growing</h3>
						<div class="space-y-2">
							${
								(data.fastest_growing || [])
									.map(
										(region, idx) => `
								<div class="flex items-center justify-between text-xs">
									<span class="text-slate-300">${idx + 1}. ${region.region || 'N/A'}</span>
									<span class="font-semibold text-blue-400">+${(region.growth_rate || 0).toFixed(2)}%</span>
								</div>
							`
									)
									.join('') || '<p class="text-xs text-slate-500">No data available</p>'
							}
						</div>
					</div>
				</div>
				
				<!-- Lagging Regions -->
				${
					data.lagging_regions && data.lagging_regions.length > 0
						? `
					<div class="bg-slate-800/60 rounded-xl p-4 border border-slate-700">
						<h3 class="text-sm font-semibold mb-3 text-yellow-400">Regions Needing Improvement</h3>
						<div class="space-y-2">
							${data.lagging_regions
								.map(
									(region, idx) => `
								<div class="flex items-center justify-between text-xs">
									<span class="text-slate-300">${idx + 1}. ${region.region || 'N/A'}</span>
									<span class="font-semibold text-yellow-400">${(region.current_value || 0).toFixed(2)}%</span>
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
	} catch (error) {
		console.error('Failed to load dashboard:', error);
		container.innerHTML = `
			<section class="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
				<h2 class="text-lg font-semibold mb-4">Dashboard</h2>
				<p class="text-sm text-red-400">Error loading dashboard: ${error.message}</p>
			</section>
		`;
	}
}
