// Additional Visualizations component (Heatmap, Map, and Animations)
// Now each chart loads independently
async function loadAdditionalVisualizations() {
	const container = document.getElementById('additional-visualizations-container');

	// Create container HTML with placeholders for each chart
	container.innerHTML = `
        <section class="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-6">
            <h2 class="text-lg font-semibold">Additional Visualizations</h2>
            
            <!-- Heatmap Chart -->
            <div id="heatmap-chart-container">
                <div class="text-center py-4">
                    <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-sky-500"></div>
                    <p class="text-sm text-slate-400 mt-2">Loading heatmap...</p>
                </div>
            </div>
            
            <!-- Animated Map Chart -->
            <div id="animated-map-chart-container">
                <div class="text-center py-4">
                    <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-sky-500"></div>
                    <p class="text-sm text-slate-400 mt-2">Loading animated map...</p>
                </div>
            </div>
            
            <!-- Animated Bar Chart -->
            <div id="animated-bar-chart-container">
                <div class="text-center py-4">
                    <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-sky-500"></div>
                    <p class="text-sm text-slate-400 mt-2">Loading animated bar chart...</p>
                </div>
            </div>
        </section>
    `;

	// Load each chart independently (don't wait for others)
	loadHeatmapChart();
	loadAnimatedMapChart();
	loadAnimatedBarChart();
}
