// Utility functions
function createMetricTooltip(description) {
	return `
		<span class="relative group">
			<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-help-circle w-3 h-3 text-slate-500 cursor-help">
				<circle cx="12" cy="12" r="10"/>
				<path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
				<path d="M12 17h.01"/>
			</svg>
			<span class="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 w-max px-3 py-2 bg-slate-700 text-white text-xs rounded-md opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-50">
				${description}
			</span>
		</span>
	`;
}

function renderPlotlyChart(chartId, plotData, options = {}) {
	const element = document.getElementById(chartId);
	if (!element) {
		console.error(`Element ${chartId} not found in DOM`);
		return;
	}

	const defaultOptions = {
		responsive: true,
		displayModeBar: true,
		displaylogo: false
	};

	try {
		// Extract data, layout, and frames from plotData
		const data = plotData.data || [];
		const layout = plotData.layout || {};
		const frames = plotData.frames || null;

		// Create plot configuration
		const config = { ...defaultOptions, ...options };

		// If frames exist, use Plotly.newPlot with frames for animation support
		if (frames && frames.length > 0) {
			Plotly.newPlot(chartId, { data, layout, frames }, config);
		} else {
			Plotly.newPlot(chartId, data, layout, config);
		}
	} catch (error) {
		console.error(`Error rendering chart ${chartId}:`, error);
		element.innerHTML = `<p class="text-red-400">Error rendering chart: ${error.message}</p>`;
	}
}
