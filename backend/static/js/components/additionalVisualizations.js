// Additional Visualizations component (Heatmap and Map)
async function loadAdditionalVisualizations() {
	try {
		const [heatmapResponse, mapResponse] = await Promise.all([
			API.heatmap(),
			API.map()
		]);

		let html =
			'<section class="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-6"><h2 class="text-lg font-semibold">Additional Visualizations</h2>';

		// Render Heatmap
		if (heatmapResponse.error) {
			html += `
                <div class="bg-red-900/20 border border-red-800 rounded-xl p-4">
                    <p class="text-red-400">Error loading heatmap: ${heatmapResponse.error}</p>
                </div>
            `;
		} else if (heatmapResponse.plot) {
			const plotData = heatmapResponse.plot;

			if (plotData.data && Array.isArray(plotData.data) && plotData.data.length > 0) {
				const chartId = 'heatmap-chart';
				html += `
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
				}, 500);
			} else {
				html += `
                    <div class="bg-yellow-900/20 border border-yellow-800 rounded-xl p-4">
                        <p class="text-yellow-400">Heatmap data is empty or invalid</p>
                    </div>
                `;
			}
		} else {
			html += `
                <div class="bg-yellow-900/20 border border-yellow-800 rounded-xl p-4">
                    <p class="text-yellow-400">No heatmap data received from server</p>
                </div>
            `;
		}

		// Render Map
		if (mapResponse.error) {
			html += `
                <div class="bg-red-900/20 border border-red-800 rounded-xl p-4">
                    <p class="text-red-400">Error loading map: ${mapResponse.error}</p>
                </div>
            `;
		} else if (mapResponse.plot) {
			const plotData = mapResponse.plot;

			if (plotData.data && Array.isArray(plotData.data) && plotData.data.length > 0) {
				const chartId = 'map-chart';
				html += `
                    <div>
                        <h3 class="text-sm font-semibold mb-3">Interactive Regional Map</h3>
                        <div class="bg-slate-800/60 rounded-xl p-4">
                            <div id="${chartId}" style="min-height: 400px;"></div>
                        </div>
                    </div>
                `;
				setTimeout(() => {
					renderPlotlyChart(chartId, plotData);
				}, 600);
			} else {
				html += `
                    <div class="bg-yellow-900/20 border border-yellow-800 rounded-xl p-4">
                        <p class="text-yellow-400">Map data is empty or invalid</p>
                    </div>
                `;
			}
		} else {
			html += `
                <div class="bg-yellow-900/20 border border-yellow-800 rounded-xl p-4">
                    <p class="text-yellow-400">No map data received from server</p>
                </div>
            `;
		}

		html += '</section>';
		document.getElementById('additional-visualizations-container').innerHTML = html;
	} catch (error) {
		console.error('Failed to load additional visualizations:', error);
		document.getElementById('additional-visualizations-container').innerHTML = `
            <section class="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
                <h2 class="text-lg font-semibold">Additional Visualizations</h2>
                <div class="bg-red-900/20 border border-red-800 rounded-xl p-4 mt-4">
                    <p class="text-red-400">Error: ${error.message}</p>
                </div>
            </section>
        `;
	}
}

