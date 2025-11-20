// Animated Map Chart component
async function loadAnimatedMapChart() {
	const containerId = 'animated-map-chart-container';
	try {
		const response = await API.animatedMap();

		if (response.error) {
			document.getElementById(containerId).innerHTML = `
                <div class="bg-red-900/20 border border-red-800 rounded-xl p-4">
                    <p class="text-red-400">Error loading animated map: ${response.error}</p>
                </div>
            `;
			return;
		}

		if (response.plot) {
			const plotData = response.plot;

			if (plotData.data && Array.isArray(plotData.data) && plotData.data.length > 0) {
				const chartId = 'animated-map-chart';
				document.getElementById(containerId).innerHTML = `
                    <div>
                        <h3 class="text-sm font-semibold mb-3">Animated Regional Map (Year-by-Year Evolution)</h3>
                        <p class="text-xs text-slate-400 mb-3">Watch how renewable energy adoption evolves across regions over time. Use the play button or slider to control the animation.</p>
                        <div class="bg-slate-800/60 rounded-xl p-4">
                            <div id="${chartId}" style="min-height: 400px;"></div>
                        </div>
                    </div>
                `;
				setTimeout(() => {
					renderPlotlyChart(chartId, plotData);
				}, 300);
			} else {
				document.getElementById(containerId).innerHTML = `
                    <div class="bg-yellow-900/20 border border-yellow-800 rounded-xl p-4">
                        <p class="text-yellow-400">Animated map data is empty or invalid</p>
                    </div>
                `;
			}
		} else {
			document.getElementById(containerId).innerHTML = `
                <div class="bg-yellow-900/20 border border-yellow-800 rounded-xl p-4">
                    <p class="text-yellow-400">No animated map data received from server</p>
                </div>
            `;
		}
	} catch (error) {
		console.error('Failed to load animated map:', error);
		document.getElementById(containerId).innerHTML = `
            <div class="bg-red-900/20 border border-red-800 rounded-xl p-4">
                <p class="text-red-400">Error: ${error.message}</p>
            </div>
        `;
	}
}
