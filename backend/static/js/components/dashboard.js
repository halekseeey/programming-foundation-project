// Dashboard component - Main Insights
async function renderDashboard() {
	const container = document.getElementById('dashboard-container');
	if (!container) return;

	try {
		// Load data from existing analytics
		const [globalTrends, regionsRanking, energySources] = await Promise.all([
			API.globalTrends(),
			API.regionsRanking(),
			API.energySources()
		]);

		// Extract key metrics
		const avgGrowthRate = globalTrends.overall_growth_rate || 0;
		const trendDirection = globalTrends.trend_direction || 'stable';
		const topRegions = globalTrends.top_regions || [];
		const leadingRegions = regionsRanking.leading_by_value || [];
		const fastestGrowing = regionsRanking.fastest_growing || [];
		// Get top energy sources by share_of_total
		const topEnergySources = (energySources.sources || [])
			.sort((a, b) => (b.share_of_total || 0) - (a.share_of_total || 0))
			.slice(0, 3);

		// Calculate average renewable percentage
		const avgRenewable =
			topRegions.length > 0 ? (topRegions.reduce((sum, r) => sum + r.average, 0) / topRegions.length).toFixed(1) : 'N/A';

		// Get period
		const period = globalTrends.period || {};
		const periodText = period.from && period.to ? `${period.from}-${period.to}` : 'All available years';

		// Build insights
		const insights = [];

		if (trendDirection === 'increasing') {
			insights.push(`Renewable energy adoption is ${trendDirection} across EU regions`);
		} else if (trendDirection === 'decreasing') {
			insights.push(`Renewable energy adoption shows a ${trendDirection} trend`);
		} else {
			insights.push(`Renewable energy adoption remains ${trendDirection}`);
		}

		if (leadingRegions.length > 0) {
			insights.push(
				`${leadingRegions[0].region} leads with ${leadingRegions[0].last_value?.toFixed(1) || 'N/A'}% renewable energy`
			);
		}

		if (fastestGrowing.length > 0 && fastestGrowing[0].total_change_pct > 0) {
			insights.push(
				`${fastestGrowing[0].region} shows fastest growth (+${fastestGrowing[0].total_change_pct.toFixed(1)}%)`
			);
		}

		if (topEnergySources.length > 0) {
			insights.push(`${topEnergySources[0].source} is the most common renewable energy source`);
		}

		// Render dashboard
		container.innerHTML = `
			<section class="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-6">
				<h2 class="text-lg font-semibold">Dashboard - Main Insights</h2>
				<p class="text-xs text-slate-400">💡 This dashboard provides a quick overview of key renewable energy trends and top-performing regions. Use the filters below to explore detailed comparisons.</p>
				
				<!-- Key Metrics Grid -->
				<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
					<!-- Average Renewable Energy -->
					<div class="bg-slate-800/60 rounded-xl p-4">
						<p class="text-xs text-slate-400 mb-1">Average Renewable Energy</p>
						<p class="text-2xl font-bold text-green-400">${avgRenewable}%</p>
						<p class="text-xs text-slate-500 mt-1">Across top regions</p>
					</div>

					<!-- Growth Rate -->
					<div class="bg-slate-800/60 rounded-xl p-4">
						<p class="text-xs text-slate-400 mb-1">Overall Growth Rate</p>
						<p class="text-2xl font-bold ${avgGrowthRate >= 0 ? 'text-green-400' : 'text-red-400'}">
							${avgGrowthRate >= 0 ? '+' : ''}${avgGrowthRate.toFixed(2)}
						</p>
						<p class="text-xs text-slate-500 mt-1">per year (${periodText})</p>
					</div>

					<!-- Trend Direction -->
					<div class="bg-slate-800/60 rounded-xl p-4">
						<p class="text-xs text-slate-400 mb-1">Trend Direction</p>
						<p class="text-2xl font-bold ${
							trendDirection === 'increasing'
								? 'text-green-400'
								: trendDirection === 'decreasing'
								? 'text-red-400'
								: 'text-yellow-400'
						}">
							${trendDirection.toUpperCase()}
						</p>
						<p class="text-xs text-slate-500 mt-1">Overall trend</p>
					</div>
				</div>

				<!-- Top Regions -->
				<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
					<!-- Leading Regions -->
					<div class="bg-slate-800/60 rounded-xl p-4">
						<h3 class="text-sm font-semibold mb-3">Top Regions by Renewable Energy</h3>
						<div class="space-y-2">
							${leadingRegions
								.slice(0, 5)
								.map(
									(region, idx) => `
								<div class="flex items-center justify-between text-sm">
									<div class="flex items-center gap-2">
										<span class="text-slate-400">${idx + 1}.</span>
										<span class="text-slate-300">${region.region}</span>
									</div>
									<span class="font-semibold text-green-400">${region.last_value?.toFixed(1) || 'N/A'}%</span>
								</div>
							`
								)
								.join('')}
						</div>
					</div>

					<!-- Fastest Growing -->
					<div class="bg-slate-800/60 rounded-xl p-4">
						<h3 class="text-sm font-semibold mb-3">Fastest Growing Regions</h3>
						<div class="space-y-2">
							${fastestGrowing
								.slice(0, 5)
								.map(
									(region, idx) => `
								<div class="flex items-center justify-between text-sm">
									<div class="flex items-center gap-2">
										<span class="text-slate-400">${idx + 1}.</span>
										<span class="text-slate-300">${region.region}</span>
									</div>
									<span class="font-semibold text-sky-400">+${region.total_change_pct?.toFixed(1) || 'N/A'}%</span>
								</div>
							`
								)
								.join('')}
						</div>
					</div>
				</div>

				<!-- Key Insights -->
				<div class="bg-slate-800/60 rounded-xl p-4">
					<h3 class="text-sm font-semibold mb-3">Key Insights</h3>
					<ul class="space-y-2">
						${insights
							.map(
								(insight) => `
							<li class="text-sm text-slate-300 flex items-start gap-2">
								<span class="text-sky-400 mt-1">•</span>
								<span>${insight}</span>
							</li>
						`
							)
							.join('')}
					</ul>
				</div>
			</section>
		`;
	} catch (error) {
		console.error('Failed to load dashboard:', error);
		container.innerHTML = `
			<section class="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
				<h2 class="text-lg font-semibold mb-4">Dashboard - Main Insights</h2>
				<p class="text-sm text-red-400">Error loading dashboard: ${error.message}</p>
			</section>
		`;
	}
}
