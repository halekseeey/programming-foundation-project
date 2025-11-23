// Filters component for region and energy type selection
let selectedRegions = [];
let selectedEnergyTypes = [];

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
						<label class="block text-sm font-medium text-slate-300 mb-2">Select Regions</label>
						<div class="relative">
							<button
								id="region-dropdown-btn"
								class="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-sky-500 flex items-center justify-between"
							>
								<span id="region-display-text">${selectedRegions.length > 0 ? `${selectedRegions.length} selected` : 'Select regions...'}</span>
								<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
								</svg>
							</button>
							<div
								id="region-dropdown"
								class="hidden absolute z-10 w-full mt-1 bg-slate-800 border border-slate-700 rounded-lg shadow-lg max-h-[300px] overflow-y-auto"
							>
								<div class="p-3 space-y-2">
									${regions
										.map(
											(r) => `
										<label class="flex items-center space-x-2 cursor-pointer hover:bg-slate-700/50 rounded px-2 py-1 transition-colors">
											<input 
												type="checkbox" 
												value="${r}" 
												class="region-checkbox w-4 h-4 text-sky-600 bg-slate-700 border-slate-600 rounded focus:ring-sky-500 focus:ring-2"
												${selectedRegions.includes(r) ? 'checked' : ''}
											>
											<span class="text-sm text-slate-300">${r}</span>
										</label>
									`
										)
										.join('')}
								</div>
								<div class="border-t border-slate-700 p-2 flex gap-2">
									<button 
										id="select-all-regions-btn"
										class="text-xs px-2 py-1 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded transition-colors"
									>
										Select All
									</button>
									<button 
										id="deselect-all-regions-btn"
										class="text-xs px-2 py-1 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded transition-colors"
									>
										Deselect All
									</button>
								</div>
							</div>
						</div>
					</div>
					<div>
						<label class="block text-sm font-medium text-slate-300 mb-2">Select Energy Types</label>
						<div class="relative">
							<button
								id="energy-type-dropdown-btn"
								class="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-sky-500 flex items-center justify-between"
							>
								<span id="energy-type-display-text">${
									selectedEnergyTypes.length > 0
										? `${selectedEnergyTypes.length} selected`
										: 'Select energy types...'
								}</span>
								<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
								</svg>
							</button>
							<div
								id="energy-type-dropdown"
								class="hidden absolute z-10 w-full mt-1 bg-slate-800 border border-slate-700 rounded-lg shadow-lg max-h-[300px] overflow-y-auto"
							>
								<div class="p-3 space-y-2">
									${energyTypes
										.map(
											(e) => `
										<label class="flex items-center space-x-2 cursor-pointer hover:bg-slate-700/50 rounded px-2 py-1 transition-colors">
											<input 
												type="checkbox" 
												value="${e}" 
												class="energy-type-checkbox w-4 h-4 text-sky-600 bg-slate-700 border-slate-600 rounded focus:ring-sky-500 focus:ring-2"
												${selectedEnergyTypes.includes(e) ? 'checked' : ''}
											>
											<span class="text-sm text-slate-300">${e}</span>
										</label>
									`
										)
										.join('')}
								</div>
								<div class="border-t border-slate-700 p-2 flex gap-2">
									<button 
										id="select-all-energy-types-btn"
										class="text-xs px-2 py-1 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded transition-colors"
									>
										Select All
									</button>
									<button 
										id="deselect-all-energy-types-btn"
										class="text-xs px-2 py-1 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded transition-colors"
									>
										Deselect All
									</button>
								</div>
							</div>
						</div>
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
				<div class="selected-regions-display"></div>
			</section>
		`;

		container.innerHTML = html;

		// Setup event listeners
		const applyBtn = document.getElementById('apply-filters-btn');
		const clearBtn = document.getElementById('clear-filters-btn');
		const regionDropdownBtn = document.getElementById('region-dropdown-btn');
		const regionDropdown = document.getElementById('region-dropdown');
		const selectAllBtn = document.getElementById('select-all-regions-btn');
		const deselectAllBtn = document.getElementById('deselect-all-regions-btn');
		const energyTypeDropdownBtn = document.getElementById('energy-type-dropdown-btn');
		const energyTypeDropdown = document.getElementById('energy-type-dropdown');
		const selectAllEnergyTypesBtn = document.getElementById('select-all-energy-types-btn');
		const deselectAllEnergyTypesBtn = document.getElementById('deselect-all-energy-types-btn');
		const energyTypeCheckboxes = document.querySelectorAll('.energy-type-checkbox');
		const regionCheckboxes = document.querySelectorAll('.region-checkbox');

		// Region dropdown toggle
		if (regionDropdownBtn && regionDropdown) {
			regionDropdownBtn.addEventListener('click', (e) => {
				e.stopPropagation();
				regionDropdown.classList.toggle('hidden');
			});

			// Close dropdown when clicking outside
			document.addEventListener('click', (e) => {
				if (!regionDropdown.contains(e.target) && !regionDropdownBtn.contains(e.target)) {
					regionDropdown.classList.add('hidden');
				}
			});
		}

		// Update selected regions when checkbox changes
		regionCheckboxes.forEach((checkbox) => {
			checkbox.addEventListener('change', () => {
				updateSelectedRegions();
			});
		});

		function updateSelectedRegions() {
			selectedRegions = Array.from(document.querySelectorAll('.region-checkbox:checked')).map((cb) => cb.value);
			const displayText = document.getElementById('region-display-text');
			if (displayText) {
				if (selectedRegions.length > 0) {
					displayText.textContent = `${selectedRegions.length} selected`;
				} else {
					displayText.textContent = 'Select regions...';
				}
			}
			// Update selected regions display
			const selectedContainer = document.querySelector('.selected-regions-display');
			if (selectedContainer) {
				if (selectedRegions.length > 0) {
					selectedContainer.innerHTML = `
						<div class="mt-4 p-3 bg-slate-800/60 rounded-lg">
							<p class="text-xs text-slate-400 mb-2">Selected regions (${selectedRegions.length}):</p>
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
					`;
				} else {
					selectedContainer.innerHTML = '';
				}
			}
		}

		if (selectAllBtn) {
			selectAllBtn.addEventListener('click', () => {
				regionCheckboxes.forEach((checkbox) => {
					checkbox.checked = true;
				});
				updateSelectedRegions();
			});
		}

		if (deselectAllBtn) {
			deselectAllBtn.addEventListener('click', () => {
				regionCheckboxes.forEach((checkbox) => {
					checkbox.checked = false;
				});
				updateSelectedRegions();
			});
		}

		// Energy type dropdown toggle
		if (energyTypeDropdownBtn && energyTypeDropdown) {
			energyTypeDropdownBtn.addEventListener('click', (e) => {
				e.stopPropagation();
				energyTypeDropdown.classList.toggle('hidden');
			});

			// Close dropdown when clicking outside
			document.addEventListener('click', (e) => {
				if (!energyTypeDropdown.contains(e.target) && !energyTypeDropdownBtn.contains(e.target)) {
					energyTypeDropdown.classList.add('hidden');
				}
			});
		}

		// Update selected energy types when checkbox changes
		energyTypeCheckboxes.forEach((checkbox) => {
			checkbox.addEventListener('change', () => {
				updateSelectedEnergyTypes();
			});
		});

		function updateSelectedEnergyTypes() {
			selectedEnergyTypes = Array.from(document.querySelectorAll('.energy-type-checkbox:checked')).map((cb) => cb.value);
			const displayText = document.getElementById('energy-type-display-text');
			if (displayText) {
				if (selectedEnergyTypes.length > 0) {
					displayText.textContent = `${selectedEnergyTypes.length} selected`;
				} else {
					displayText.textContent = 'Select energy types...';
				}
			}
		}

		if (selectAllEnergyTypesBtn) {
			selectAllEnergyTypesBtn.addEventListener('click', () => {
				energyTypeCheckboxes.forEach((checkbox) => {
					checkbox.checked = true;
				});
				updateSelectedEnergyTypes();
			});
		}

		if (deselectAllEnergyTypesBtn) {
			deselectAllEnergyTypesBtn.addEventListener('click', () => {
				energyTypeCheckboxes.forEach((checkbox) => {
					checkbox.checked = false;
				});
				updateSelectedEnergyTypes();
			});
		}

		if (applyBtn) {
			applyBtn.addEventListener('click', async () => {
				// Get all selected regions from checkboxes
				selectedRegions = Array.from(document.querySelectorAll('.region-checkbox:checked')).map((cb) => cb.value);
				selectedEnergyTypes = Array.from(document.querySelectorAll('.energy-type-checkbox:checked')).map(
					(cb) => cb.value
				);

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
				selectedEnergyTypes = [];
				// Clear all checkboxes
				regionCheckboxes.forEach((checkbox) => {
					checkbox.checked = false;
				});
				energyTypeCheckboxes.forEach((checkbox) => {
					checkbox.checked = false;
				});
				const filteredContainer = document.getElementById('filtered-analysis-container');
				if (filteredContainer) {
					filteredContainer.style.display = 'none';
				}
				updateSelectedRegions();
				updateSelectedEnergyTypes();
			});
		}

		// Initial update
		updateSelectedEnergyTypes();

		// Initial update of selected regions display
		updateSelectedRegions();
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

	// Ensure variables are defined and updated from checkboxes
	if (typeof selectedRegions === 'undefined') {
		selectedRegions = [];
	}
	if (typeof selectedEnergyTypes === 'undefined') {
		selectedEnergyTypes = [];
	}

	// Update from checkboxes to ensure we have the latest values
	selectedRegions = Array.from(document.querySelectorAll('.region-checkbox:checked')).map((cb) => cb.value);
	selectedEnergyTypes = Array.from(document.querySelectorAll('.energy-type-checkbox:checked')).map((cb) => cb.value);

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
		const filteredData = await API.getFilteredVisualizations(selectedRegions, selectedEnergyTypes);

		if (filteredData.error) {
			chartsContainer.innerHTML = `
				<div class="bg-red-900/20 border border-red-800 rounded-xl p-4">
					<p class="text-red-400">${filteredData.error}</p>
				</div>
			`;
			return;
		}

		let html = '';

		// Display errors if any (but still show available charts)
		if (filteredData.errors && filteredData.errors.length > 0) {
			html += `
				<div class="bg-yellow-900/20 border border-yellow-800 rounded-xl p-4 mb-4">
					<p class="text-yellow-400 font-semibold mb-2">Warning:</p>
					<ul class="list-disc list-inside space-y-1 text-yellow-300">
						${filteredData.errors.map((err) => `<li>${err}</li>`).join('')}
					</ul>
				</div>
			`;
		}

		// Render yearly trends comparison chart (if regions selected)
		if (filteredData.yearly_trends_plot) {
			const chartId = 'filtered-yearly-trends';
			html += `
				<div class="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
					<h3 class="text-sm font-semibold mb-3">Yearly Trends Comparison${
						selectedRegions.length > 0 ? ` - ${selectedRegions.join(', ')}` : ''
					}</h3>
					<p class="text-xs text-slate-400 mb-3">📊 Compare energy trends across selected regions.</p>
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
					<p class="text-xs text-slate-400 mb-3">📊 Compare energy source distribution across selected regions.</p>
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
			const energyTypeLabel = selectedEnergyTypes.length > 0 ? selectedEnergyTypes.join(', ') : 'Selected Energy Types';
			html += `
				<div class="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
					<h3 class="text-sm font-semibold mb-3">${energyTypeLabel} Trends Across Regions</h3>
					<p class="text-xs text-slate-400 mb-3">📊 Track how selected energy types evolve across regions over time.</p>
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

		// Add download button if there are charts
		if (
			filteredData.yearly_trends_plot ||
			filteredData.sources_distribution_plot ||
			filteredData.energy_type_timeseries_plot
		) {
			html =
				`
				<div class="flex items-center justify-between mb-4">
					<h4 class="text-sm font-semibold text-slate-300">Download Options</h4>
					<div class="flex gap-2">
						<button 
							id="download-charts-btn"
							class="px-3 py-1.5 bg-green-600 hover:bg-green-700 text-white text-xs font-semibold rounded-lg transition-colors flex items-center gap-2"
							title="Download all charts as PNG images"
						>
							<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
								<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
								<polyline points="7 10 12 15 17 10"></polyline>
								<line x1="12" y1="15" x2="12" y2="3"></line>
							</svg>
							Download Charts
						</button>
						<button 
							id="download-data-btn"
							class="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg transition-colors flex items-center gap-2"
							title="Download filtered data as CSV"
						>
							<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
								<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
								<polyline points="7 10 12 15 17 10"></polyline>
								<line x1="12" y1="15" x2="12" y2="3"></line>
							</svg>
							Download Data
						</button>
					</div>
				</div>
			` + html;
		}

		chartsContainer.innerHTML = html;

		// Setup download handlers after charts are rendered
		setTimeout(() => {
			setupDownloadHandlers(selectedRegions, selectedEnergyTypes);
		}, 500);
	} catch (error) {
		console.error('Failed to apply filters:', error);
		chartsContainer.innerHTML = `
			<div class="bg-red-900/20 border border-red-800 rounded-xl p-4">
				<p class="text-red-400">Error applying filters: ${error.message}</p>
			</div>
		`;
	}
}

function setupDownloadHandlers(selectedRegions, selectedEnergyTypes) {
	// Download charts button
	const downloadChartsBtn = document.getElementById('download-charts-btn');
	if (downloadChartsBtn) {
		downloadChartsBtn.addEventListener('click', async () => {
			try {
				const chartIds = [
					{ id: 'filtered-yearly-trends', name: 'yearly_trends' },
					{ id: 'filtered-sources-distribution', name: 'sources_distribution' },
					{ id: 'filtered-energy-type-timeseries', name: 'energy_type_timeseries' }
				];

				let downloaded = 0;
				for (const chart of chartIds) {
					const chartElement = document.getElementById(chart.id);
					if (chartElement && chartElement.data && chartElement.data.length > 0) {
						try {
							await Plotly.downloadImage(chartElement, {
								format: 'png',
								width: 1200,
								height: 600,
								filename: `filtered_${chart.name}_${Date.now()}`
							});
							downloaded++;
							// Small delay between downloads
							await new Promise((resolve) => setTimeout(resolve, 500));
						} catch (err) {
							console.warn(`Failed to download ${chart.name}:`, err);
						}
					}
				}

				if (downloaded === 0) {
					alert('No charts available to download. Please wait for charts to load.');
				} else {
					alert(`Successfully downloaded ${downloaded} chart(s).`);
				}
			} catch (error) {
				console.error('Failed to download charts:', error);
				alert('Error downloading charts. Please try again.');
			}
		});
	}

	// Download data button
	const downloadDataBtn = document.getElementById('download-data-btn');
	if (downloadDataBtn) {
		downloadDataBtn.addEventListener('click', async () => {
			try {
				// Get filtered data from API
				const params = new URLSearchParams();
				if (selectedRegions && selectedRegions.length > 0) {
					params.append('regions', selectedRegions.join(','));
				}
				if (selectedEnergyTypes && selectedEnergyTypes.length > 0) {
					params.append('energy_types', selectedEnergyTypes.join(','));
				}

				const response = await fetch(`${window.location.origin}/api/analysis/filtered/data?${params.toString()}`);
				if (!response.ok) {
					throw new Error(`HTTP error! status: ${response.status}`);
				}

				const blob = await response.blob();
				const url = window.URL.createObjectURL(blob);
				const a = document.createElement('a');
				a.href = url;
				const filename = `filtered_data_${selectedRegions.join('_') || 'all_regions'}_${
					selectedEnergyTypes.join('_') || 'all_types'
				}_${Date.now()}.csv`;
				a.download = filename;
				document.body.appendChild(a);
				a.click();
				document.body.removeChild(a);
				window.URL.revokeObjectURL(url);
			} catch (error) {
				console.error('Failed to download data:', error);
				alert('Error downloading data. Please try again.');
			}
		});
	}
}
