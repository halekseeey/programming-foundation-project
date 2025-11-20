// Animated Bar Chart component
async function loadAnimatedBarChart() {
	const containerId = 'animated-bar-chart-container';
	try {
		const response = await API.animatedBar();

		if (response.error) {
			document.getElementById(containerId).innerHTML = `
                <div class="bg-red-900/20 border border-red-800 rounded-xl p-4">
                    <p class="text-red-400">Error loading animated bar chart: ${response.error}</p>
                </div>
            `;
			return;
		}

		if (response.plot) {
			const plotData = response.plot;

			if (plotData.data && Array.isArray(plotData.data) && plotData.data.length > 0) {
				const chartId = 'animated-bar-chart';
				document.getElementById(containerId).innerHTML = `
                    <div>
                        <h3 class="text-sm font-semibold mb-3">Animated Regional Bar Chart (Year-by-Year Evolution)</h3>
                        <p class="text-xs text-slate-400 mb-3">See how renewable energy share changes across top regions year by year. Use the play button or slider to control the animation.</p>
                        <div class="bg-slate-800/60 rounded-xl p-4">
                            <div id="${chartId}" style="min-height: 400px;"></div>
                        </div>
                    </div>
                `;
				setTimeout(() => {
					renderPlotlyChart(chartId, plotData);
				}, 400);
			} else {
				document.getElementById(containerId).innerHTML = `
                    <div class="bg-yellow-900/20 border border-yellow-800 rounded-xl p-4">
                        <p class="text-yellow-400">Animated bar chart data is empty or invalid</p>
                    </div>
                `;
			}
		} else {
			document.getElementById(containerId).innerHTML = `
                <div class="bg-yellow-900/20 border border-yellow-800 rounded-xl p-4">
                    <p class="text-yellow-400">No animated bar chart data received from server</p>
                </div>
            `;
		}
	} catch (error) {
		console.error('Failed to load animated bar chart:', error);
		document.getElementById(containerId).innerHTML = `
            <div class="bg-red-900/20 border border-red-800 rounded-xl p-4">
                <p class="text-red-400">Error: ${error.message}</p>
            </div>
        `;
	}
}
