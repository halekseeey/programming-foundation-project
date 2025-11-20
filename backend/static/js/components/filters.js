// Filters component for region and energy type selection
let selectedRegions = [];
let selectedEnergyType = null;

async function loadFilters() {
	const container = document.getElementById('filters-container');
	if (!container) return;

	try {
		const [regionsData, energyTypesData] = await Promise.all([API.getRegions(), API.getEnergyTypes()]);

		const regions = regionsData.regions || [];
		const energyTypes = energyTypesData.energy_types || [];

		let html = `
			<section class="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
				<h2 class="text-lg font-semibold mb-4">Filters</h2>
				<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
					<div>
						<label class="block text-sm font-medium text-slate-300 mb-2">Select Regions (Multiple)</label>
						<select 
							id="region-select" 
							multiple
							size="8"
							class="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-sky-500"
						>
							${regions.map((r) => `<option value="${r}">${r}</option>`).join('')}
						</select>
						<p class="text-xs text-slate-400 mt-1">Hold Ctrl/Cmd to select multiple regions</p>
					</div>
					<div>
						<label class="block text-sm font-medium text-slate-300 mb-2">Select Energy Type</label>
						<select 
							id="energy-type-select" 
							class="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-sky-500"
						>
							<option value="">All Energy Types</option>
							${energyTypes.map((e) => `<option value="${e}">${e}</option>`).join('')}
						</select>
					</div>
				</div>
				<div class="mt-4 flex gap-2">
					<button 
						id="apply-filters-btn"
						class="px-4 py-2 bg-sky-600 hover:bg-sky-700 text-white text-sm font-semibold rounded-lg transition-colors"
					>
						Apply Filters
					</button>
					<button 
						id="clear-filters-btn"
						class="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white text-sm font-semibold rounded-lg transition-colors"
					>
						Clear Filters
					</button>
				</div>
				${
					selectedRegions.length > 0
						? `
					<div class="mt-4 p-3 bg-slate-800/60 rounded-lg">
						<p class="text-xs text-slate-400 mb-2">Selected regions:</p>
						<div class="flex flex-wrap gap-2">
							${selectedRegions
								.map(
									(r) => `
								<span class="px-2 py-1 bg-sky-600/20 text-sky-300 text-xs rounded">${r}</span>
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

		// Setup event listeners
		const applyBtn = document.getElementById('apply-filters-btn');
		const clearBtn = document.getElementById('clear-filters-btn');
		const regionSelect = document.getElementById('region-select');
		const energyTypeSelect = document.getElementById('energy-type-select');

		if (applyBtn) {
			applyBtn.addEventListener('click', async () => {
				// Get all selected regions
				selectedRegions = Array.from(regionSelect.selectedOptions).map((opt) => opt.value);
				selectedEnergyType = energyTypeSelect.value || null;

				if (selectedRegions.length === 0) {
					alert('Please select at least one region');
					return;
				}

				await applyFilters();
			});
		}

		if (clearBtn) {
			clearBtn.addEventListener('click', () => {
				selectedRegions = [];
				selectedEnergyType = null;
				// Clear all selections in multi-select
				Array.from(regionSelect.options).forEach((opt) => (opt.selected = false));
				energyTypeSelect.value = '';
				const filteredContainer = document.getElementById('filtered-analysis-container');
				if (filteredContainer) {
					filteredContainer.style.display = 'none';
				}
				// Reload filters to update UI
				loadFilters();
			});
		}
	} catch (error) {
		console.error('Failed to load filters:', error);
		container.innerHTML = `
			<section class="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
				<h2 class="text-lg font-semibold mb-4">Filters</h2>
				<p class="text-sm text-red-400">Error loading filters: ${error.message}</p>
			</section>
		`;
	}
}

async function applyFilters() {
	const filteredContainer = document.getElementById('filtered-analysis-container');
	const chartsContainer = document.getElementById('filtered-charts-container');

	if (!filteredContainer || !chartsContainer) return;

	// Show loading state
	filteredContainer.style.display = 'block';
	chartsContainer.innerHTML = `
		<div class="text-center py-8">
			<div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-sky-500"></div>
			<p class="text-sm text-slate-400 mt-2">Loading filtered analysis...</p>
		</div>
	`;

	try {
		// Load filtered visualizations (works with large dataset)
		const filteredData = await API.getFilteredVisualizations(selectedRegions, selectedEnergyType);

		if (filteredData.error) {
			chartsContainer.innerHTML = `
				<div class="bg-red-900/20 border border-red-800 rounded-xl p-4">
					<p class="text-red-400">${filteredData.error}</p>
				</div>
			`;
			return;
		}

		let html = '';

		// Render yearly trends comparison chart (if regions selected)
		if (filteredData.yearly_trends_plot) {
			const chartId = 'filtered-yearly-trends';
			html += `
				<div class="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
					<h3 class="text-sm font-semibold mb-3">Yearly Trends Comparison${
						selectedRegions.length > 0 ? ` - ${selectedRegions.join(', ')}` : ''
					}</h3>
					<div class="bg-slate-800/60 rounded-xl p-4">
						<div id="${chartId}"></div>
					</div>
				</div>
			`;
			setTimeout(() => {
				renderPlotlyChart(chartId, filteredData.yearly_trends_plot);
			}, 100);
		}

		// Render energy sources distribution chart (if regions selected)
		if (filteredData.sources_distribution_plot) {
			const chartId = 'filtered-sources-distribution';
			html += `
				<div class="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
					<h3 class="text-sm font-semibold mb-3">Energy Sources Distribution${
						selectedRegions.length > 0 ? ` - ${selectedRegions.join(', ')}` : ''
					}</h3>
					<div class="bg-slate-800/60 rounded-xl p-4">
						<div id="${chartId}"></div>
					</div>
				</div>
			`;
			setTimeout(() => {
				renderPlotlyChart(chartId, filteredData.sources_distribution_plot);
			}, 200);
		}

		// Render energy type time series chart (if energy type selected)
		if (filteredData.energy_type_timeseries_plot) {
			const chartId = 'filtered-energy-type-timeseries';
			html += `
				<div class="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
					<h3 class="text-sm font-semibold mb-3">${selectedEnergyType} Trends Across Regions</h3>
					<div class="bg-slate-800/60 rounded-xl p-4">
						<div id="${chartId}"></div>
					</div>
				</div>
			`;
			setTimeout(() => {
				renderPlotlyChart(chartId, filteredData.energy_type_timeseries_plot);
			}, 300);
		}

		if (!html) {
			html = `
				<div class="bg-yellow-900/20 border border-yellow-800 rounded-xl p-4">
					<p class="text-yellow-400">No visualizations available for selected filters. Please select a region or energy type.</p>
				</div>
			`;
		}

		chartsContainer.innerHTML = html;
	} catch (error) {
		console.error('Failed to apply filters:', error);
		chartsContainer.innerHTML = `
			<div class="bg-red-900/20 border border-red-800 rounded-xl p-4">
				<p class="text-red-400">Error applying filters: ${error.message}</p>
			</div>
		`;
	}
}
