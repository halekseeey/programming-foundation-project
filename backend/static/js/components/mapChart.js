// Map Chart component
async function loadMapChart() {
	const containerId = 'map-chart-container';
	try {
		const response = await API.map();

		if (response.error) {
			document.getElementById(containerId).innerHTML = `
                <div class="bg-red-900/20 border border-red-800 rounded-xl p-4">
                    <p class="text-red-400">Error loading map: ${response.error}</p>
                </div>
            `;
			return;
		}

		if (response.plot) {
			const plotData = response.plot;

			if (plotData.data && Array.isArray(plotData.data) && plotData.data.length > 0) {
				const chartId = 'map-chart';
				document.getElementById(containerId).innerHTML = `
                    <div>
                        <h3 class="text-sm font-semibold mb-3">Interactive Regional Map</h3>
                        <div class="bg-slate-800/60 rounded-xl p-4">
                            <div id="${chartId}" style="min-height: 400px;"></div>
                        </div>
                    </div>
                `;
				setTimeout(() => {
					renderPlotlyChart(chartId, plotData);
				}, 200);
			} else {
				document.getElementById(containerId).innerHTML = `
                    <div class="bg-yellow-900/20 border border-yellow-800 rounded-xl p-4">
                        <p class="text-yellow-400">Map data is empty or invalid</p>
                    </div>
                `;
			}
		} else {
			document.getElementById(containerId).innerHTML = `
                <div class="bg-yellow-900/20 border border-yellow-800 rounded-xl p-4">
                    <p class="text-yellow-400">No map data received from server</p>
                </div>
            `;
		}
	} catch (error) {
		console.error('Failed to load map:', error);
		document.getElementById(containerId).innerHTML = `
            <div class="bg-red-900/20 border border-red-800 rounded-xl p-4">
                <p class="text-red-400">Error: ${error.message}</p>
            </div>
        `;
	}
}
