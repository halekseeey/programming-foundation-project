// Heatmap Chart component
async function loadHeatmapChart() {
	const containerId = 'heatmap-chart-container';
	try {
		const response = await API.heatmap();

		if (response.error) {
			document.getElementById(containerId).innerHTML = `
                <div class="bg-red-900/20 border border-red-800 rounded-xl p-4">
                    <p class="text-red-400">Error loading heatmap: ${response.error}</p>
                </div>
            `;
			return;
		}

		if (response.plot) {
			const plotData = response.plot;

			if (plotData.data && Array.isArray(plotData.data) && plotData.data.length > 0) {
				const chartId = 'heatmap-chart';
				document.getElementById(containerId).innerHTML = `
                    <div>
                        <h3 class="text-sm font-semibold mb-3">Regional Energy Intensity Heatmap</h3>
                        <div class="bg-slate-800/60 rounded-xl p-4 overflow-auto">
                            <div id="${chartId}" style="min-width: 100%; min-height: 400px;"></div>
                        </div>
                    </div>
                `;

				setTimeout(() => {
					const layout = {
						...plotData.layout,
						autosize: true,
						height: Math.min(800, Math.max(400, plotData.layout?.height || 600))
					};
					renderPlotlyChart(chartId, { data: plotData.data, layout });
				}, 100);
			} else {
				document.getElementById(containerId).innerHTML = `
                    <div class="bg-yellow-900/20 border border-yellow-800 rounded-xl p-4">
                        <p class="text-yellow-400">Heatmap data is empty or invalid</p>
                    </div>
                `;
			}
		} else {
			document.getElementById(containerId).innerHTML = `
                <div class="bg-yellow-900/20 border border-yellow-800 rounded-xl p-4">
                    <p class="text-yellow-400">No heatmap data received from server</p>
                </div>
            `;
		}
	} catch (error) {
		console.error('Failed to load heatmap:', error);
		document.getElementById(containerId).innerHTML = `
            <div class="bg-red-900/20 border border-red-800 rounded-xl p-4">
                <p class="text-red-400">Error: ${error.message}</p>
            </div>
        `;
	}
}
