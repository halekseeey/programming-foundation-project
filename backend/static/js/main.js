// Main application entry point - renamed for clarity
async function loadAllAnalysis() {
	try {
		const [globalTrends, energySources, regionsRanking, correlation] = await Promise.all([
			API.globalTrends(),
			API.energySources(),
			API.regionsRanking(),
			API.correlation('gdp')
		]);

		// Hide loading, show analysis
		document.getElementById('loading-section').style.display = 'none';
		document.getElementById('analysis-section').style.display = 'block';

		// Render components
		renderGlobalTrends(globalTrends);
		renderEnergySources(energySources);
		renderRegionsRanking(regionsRanking);
		renderCorrelationAnalysis(correlation);
		loadAdditionalVisualizations();

		// Setup dataset preview modal (don't load preview automatically)
		setupDatasetPreviewModal();
	} catch (error) {
		console.error('Failed to load analysis data:', error);
		document.getElementById('loading-section').innerHTML = `
            <div class="bg-red-900/20 border border-red-800 rounded-2xl p-6">
                <p class="text-red-400">Error loading data: ${error.message}</p>
            </div>
        `;
	}
}

// Initialize filters and analysis on page load
document.addEventListener('DOMContentLoaded', async () => {
	// Load dashboard first
	await renderDashboard();

	// Load filters
	await loadFilters();

	// Load main analysis
	await loadAllAnalysis();
});
